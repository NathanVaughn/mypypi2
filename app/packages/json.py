import time

import pyjson5
from loguru import logger

import app.packages.simple
from app.constants import (
    METADATA_EXTENSION,
    METADATA_KEY,
    METADATA_KEY_LEGACY,
    METADATA_KEY_LEGACY2,
)
from app.models.code_file import CodeFile
from app.models.code_file_hash import CodeFileHash
from app.models.metadata_file import MetadataFile
from app.models.metadata_file_hash import MetadataFileHash
from app.models.package import Package
from app.models.package_file import PackageFile


def add_hashes(hash_dict: dict, package_file: PackageFile) -> None:
    """
    Add hashes to a package file.
    """
    for kind, value in hash_dict.items():
        # validate that the hash kind is supported
        kind = kind.lower()
        if kind not in app.packages.simple.SUPPORTED_HASHES:
            continue

        # sqlalchemy automatically appends itself
        if isinstance(package_file, CodeFile):
            CodeFileHash(code_file=package_file, kind=kind, value=value)
        elif isinstance(package_file, MetadataFile):
            MetadataFileHash(metadata_file=package_file, kind=kind, value=value)


def _parse_single_record(record: dict, package: Package) -> CodeFile:
    """
    Parse a single record
    """
    # required fields
    filename = record["filename"]
    upstream_url = app.packages.simple.urljoin(package.repository_url, record["url"])

    # optional fields
    requires_python = record.get("requires-python", None)

    # yanked can be a boolean or a string
    yanked = record.get("yanked", False)
    if isinstance(yanked, str):
        is_yanked = True
        yanked_reason = yanked
    else:
        is_yanked = yanked
        yanked_reason = None

    # postprocessing
    version = app.packages.simple.parse_version(filename)

    # create code file
    code_file = CodeFile(
        package=package,
        filename=filename,
        upstream_url=upstream_url,
        requires_python=requires_python,
        is_yanked=is_yanked,
        yanked_reason=yanked_reason,
        version=version,
    )

    # add hashes to the code file
    hashes = record.get("hashes", {})
    add_hashes(hashes, code_file)

    # grab metadata info in order of preference
    metadata = record.get(METADATA_KEY, None)
    if metadata is None:
        metadata = record.get(METADATA_KEY_LEGACY, None)
        if metadata is None:
            metadata = record.get(METADATA_KEY_LEGACY2, None)

    # add metadata file if available
    if metadata:
        code_file.metadata_file = MetadataFile(
            package=package,
            filename=f"{filename}{METADATA_EXTENSION}",
            upstream_url=f"{upstream_url}{METADATA_EXTENSION}",
            version=version,
            code_file=code_file,
        )

        # if there were hashes, add them
        if isinstance(metadata, dict):
            add_hashes(metadata, code_file.metadata_file)

    return code_file


def parse_simple_json(json_content: str, package: Package) -> list[CodeFile]:
    """
    Parse the simple registry JSON content.
    Return a list of code files.
    """
    logger.info(f"Parsing {package.repository_url} JSON content")
    start_time = time.time()

    # parse the JSON content
    # let any exceptions bubble up
    # use pyjson5 for performance
    data = pyjson5.loads(json_content)

    # tried using threadpoolexecutor, but it was slower
    code_files = [_parse_single_record(record, package) for record in data["files"]]

    end_time = time.time()
    logger.info(f"Parsing {package.repository_url} JSON content took {
                end_time - start_time:.2f} seconds")

    return code_files

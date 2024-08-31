# basically no indexes other than PyPi support the JSON format
import pyjson5

import app.packages.simple
from app.constants import (
    METADATA_EXTENSION,
    METADATA_KEY,
    METADATA_KEY_LEGACY,
    METADATA_KEY_LEGACY2,
)
from app.models.code_file import CodeFile
from app.models.metadata_file import MetadataFile
from app.models.package import Package
from app.models.package_file import PackageFile
from app.models.package_file_hash import PackageFileHash


def add_hashes(hash_dict: dict, package_file: PackageFile) -> None:
    """
    Add hashes to a package file.
    """
    for kind, value in hash_dict.items():
        # validate that the hash kind is supported
        kind = kind.lower()
        if kind not in app.packages.simple.SUPPORTED_HASHES:
            continue

        package_file.hashes.append(
            PackageFileHash(
                package_file=package_file, kind=kind, value=value)
        )


def parse_simple_json(json_content: str, url: str, package: Package) -> list[CodeFile]:
    """
    Parse the simple registry JSON content.
    Return a list of code files.
    """
    # parse the JSON content
    # let any exceptions bubble up
    # use pyjson5 for performance
    data = pyjson5.loads(json_content)

    # hold a list of records we parse
    code_files: list[CodeFile] = []

    # iterate over all records
    for record in data["files"]:
        # required fields
        filename = record["filename"]
        upstream_url = app.packages.simple.urljoin(url, record["url"])

        # optional fields
        requires_python = record.get("requires-python", None)
        yanked = record.get("yanked", None)

        # postprocessing
        version = app.packages.simple.parse_version(filename)

        # create code file
        code_file = CodeFile(
            package=package,
            filename=filename,
            upstream_url=upstream_url,
            requires_python=requires_python,
            yanked=yanked,
            version=version,
        )
        code_files.append(code_file)

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
                code_file=code_file,
            )

            # if there were hashes, add them
            if isinstance(metadata, dict):
                add_hashes(metadata, code_file.metadata_file)

    return code_files

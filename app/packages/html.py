import html
from urllib.parse import urldefrag, urljoin

import lxml.html

from app.constants import METDATA_EXTENSION
from app.models.code_file import CodeFile
from app.models.metadata_file import MetadataFile
from app.models.repository import Repository
from app.packages.simple import SUPPORTED_HASHES


def parse_hash(given: str) -> tuple[str | None, str | None]:
    """
    Parses a hash string into a tuple of hash type and hash value.
    If unsupported hash type is found, returns None.

    Expects:
    sha256=value
    md5=value
    """

    # make sure there is a seperator
    if "=" not in given:
        return None, None

    hash_type, sep, hash_value = given.partition("=")

    # make sure there is a seperator
    if sep != "=":
        return None, None

    # check if the hash type is supported
    if hash_type not in SUPPORTED_HASHES:
        return None, None

    return hash_type, hash_value


def parse_simple_html(
    html_content: str, html_url: str, repository: Repository, package_name: str
) -> tuple[list[CodeFile], list[MetadataFile]]:
    """
    Parse the simple registry HTML content.
    Return a tuple which contains a list of code files and a list of metadata files.
    """

    # use lxml for performance
    upstream_tree = lxml.html.fromstring(html_content).contents

    # hold a list of records we parse
    new_package_code_files: list[CodeFile] = []
    new_package_metadata_files: list[MetadataFile] = []

    # iterate over all anchor tags
    for anchor_tag in upstream_tree.iter("a"):
        # inner text is filename
        filename = anchor_tag.text

        # get upstream url and make it absolute
        href = anchor_tag.attrib["href"]
        absolute_href = urljoin(html_url, href)

        # parse out the hash which should be in the fragment
        upstream_url, fragment = urldefrag(absolute_href)
        if fragment:
            upstream_hash_type, upstream_hash_value = parse_hash(fragment)
        else:
            upstream_hash_type = None
            upstream_hash_value = None

        # get python requires
        requires_python = anchor_tag.attrib.get("data-requires-python", None)
        if isinstance(requires_python, str):
            requires_python = html.unescape(requires_python)

        # grab the sha256 hash from the data-dist-info-metadata attribute
        # PEP 714
        # data-core-metadata is the preferred value
        # data-dist-info-metadata is the fallback
        metadata_value = anchor_tag.attrib.get(
            "data-core-metadata", anchor_tag.attrib.get("data-dist-info-metadata", "")
        )

        # "true" is an acceptable value
        metadata_hash_type, metadata_hash_value = None, None
        if metadata_value:
            metadata_hash_type, metadata_hash_value = parse_hash(metadata_value)

        # create code file
        package_code_file = CodeFile(
            repository=repository,
            package_name=package_name,
            filename=filename,
            hash_type=upstream_hash_type,
            hash_value=upstream_hash_value,
            upstream_url=upstream_url,
            requires_python=requires_python,
        )
        new_package_code_files.append(package_code_file)

        # create metadata file
        if metadata_value:
            metadata_filename = filename + METDATA_EXTENSION
            package_metadata_file = MetadataFile(
                repository=repository,
                package_name=package_name,
                filename=metadata_filename,
                hash_type=metadata_hash_type,
                hash_value=metadata_hash_value,
                upstream_url=upstream_url + METDATA_EXTENSION,
                code_file=package_code_file,
            )
            new_package_metadata_files.append(package_metadata_file)

    return new_package_code_files, new_package_metadata_files

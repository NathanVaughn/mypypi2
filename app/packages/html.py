import html
from urllib.parse import urldefrag

import lxml.html

import app.packages.simple
from app.constants import (
    DATA_PREFIX,
    METADATA_EXTENSION,
    METADATA_KEY,
    METADATA_KEY_LEGACY,
)
from app.models.code_file import CodeFile
from app.models.metadata_file import MetadataFile
from app.models.package import Package
from app.models.package_file import PackageFile
from app.models.package_file_hash import PackageFileHash


def add_hash(given: str, package_file: PackageFile) -> None:
    """
    Parses a hash string into a tuple of hash type and hash value.
    If unsupported hash type is found, returns None.

    Expects:
    sha256=value
    md5=value
    """

    # make sure there is a seperator
    if "=" not in given:
        return

    kind, sep, value = given.partition("=")
    kind = kind.lower()

    # make sure there is a seperator
    if sep != "=":
        return

    # check if the hash type is supported
    if kind not in app.packages.simple.SUPPORTED_HASHES:
        return

    package_file.hashes.append(PackageFileHash(
        package_file=package_file, kind=kind, value=value))


def parse_simple_html(
    html_content: str, url: str, package: Package
) -> list[CodeFile]:
    """
    Parse the simple registry HTML content.
    Return a list of code files.
    """

    # use lxml for performance
    # let any exceptions bubble up
    upstream_tree = lxml.html.fromstring(html_content).contents

    # hold a list of records we parse
    code_files: list[CodeFile] = []

    # iterate over all anchor tags
    for anchor in upstream_tree.iter("a"):
        # required fields
        # inner text is filename
        filename: str = anchor.text

        # get upstream url and make it absolute
        href: str = anchor.attrib["href"]
        upstream_url = app.packages.simple.absoluify_url(url, href)

        # parse out the hash which should be in the fragment
        upstream_url, upstream_fragment = urldefrag(upstream_url)

        # optional fields
        # get python requires
        requires_python = anchor.attrib.get(
            f"{DATA_PREFIX}requires-python", None)
        if isinstance(requires_python, str):
            requires_python = html.unescape(requires_python)

        # get yanked reason
        yanked = anchor.attrib.get(f"{DATA_PREFIX}yanked", None)

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

        # add a hash to the code file
        if upstream_fragment:
            add_hash(upstream_fragment, code_file)

        # grab metadata info in order of preference
        metadata: str | None = anchor.attrib.get(
            f"{DATA_PREFIX}{METADATA_KEY}", None)
        if metadata is None:
            metadata = anchor.attrib.get(
                f"{DATA_PREFIX}{METADATA_KEY_LEGACY}", None)

        # "true" is an acceptable value
        # not guaranteed to be a "sha256=value" format
        if metadata:
            code_file.metadata_file = MetadataFile(
                package=package,
                filename=f"{filename}{METADATA_EXTENSION}",
                upstream_url=f"{upstream_url}{METADATA_EXTENSION}",
                code_file=code_file,
            )

            # if there was a hash, add it
            if "=" in metadata:
                add_hash(metadata, code_file.metadata_file)

    return code_files

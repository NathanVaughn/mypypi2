import html
from urllib.parse import urljoin

import lxml.html
from loguru import logger

import app.data.proxy
import app.data.sql
import app.data.storage.active
import app.models.exceptions
from app.constants import METDATA_EXTENSION
from app.models.code_file import CodeFile
from app.models.metadata_file import MetadataFile
from app.models.package_file import PackageFile
from app.models.repository import Repository
from app.utils import log_package_name

# https://github.com/pypa/pip/blob/b989e6ef04810bbd4033a3683020bd4ddcbdb627/src/pip/_internal/models/link.py#L40
SUPPORTED_HASHES = ("sha512", "sha384", "sha256", "sha224", "sha1", "md5")


def parse_hash(given: str) -> tuple[str | None, str | None]:
    """
    Parses a hash string into a tuple of hash type and hash value.
    If unsupported hash type is found, returns None.
    """

    # make sure there is a seperator
    if "=" not in given:
        return None, None

    # check if the hash type is supported
    if not any(given.startswith(h) for h in SUPPORTED_HASHES):
        return None, None

    for hash_type in SUPPORTED_HASHES:
        if given.startswith(hash_type):
            return hash_type, given.split("=")[1]

    # this should never happen
    return None, None


def parse_simple_registry(repository: Repository, package_name: str) -> None:
    """
    Parse the simple data from the registry.
    """
    # load metadata from simple endpoint
    package_simple_url = f"{repository.simple_url}/{package_name}/"

    # use lxml for performance
    upstream_tree = lxml.html.fromstring(
        app.data.proxy.fetch_url(repository, package_simple_url).contents
    )

    # hold a list of records we parse
    new_package_code_files: list[CodeFile] = []
    new_package_metadata_files: list[MetadataFile] = []

    # iterate over all anchor tags
    for anchor_tag in upstream_tree.iter("a"):
        # inner text is filename
        filename = anchor_tag.text

        # get upstream url and file hash
        href = anchor_tag.attrib["href"]
        absolute_href = urljoin(package_simple_url, href)
        if "#" in absolute_href:
            upstream_url = absolute_href.split("#")[0]
            upstream_hash_type, upstream_hash_value = parse_hash(
                absolute_href.split("#")[1]
            )
        else:
            upstream_url = absolute_href
            upstream_hash_type = None
            upstream_hash_value = None

        # get python requires
        requires_python = html.unescape(
            anchor_tag.attrib.get("data-requires-python", "")
        )

        # grab the sha256 hash from the data-dist-info-metadata attribute
        # PEP 714
        # data-core-metadata is the preferred value
        # data-dist-info-metadata is the fallback
        metadata_value = anchor_tag.attrib.get(
            "data-core-metadata", anchor_tag.attrib.get("data-dist-info-metadata", "")
        )

        # true is an acceptable value
        metadata_hash_type, metadata_hash_value = None, None
        if metadata_value:
            metadata_hash_type, metadata_hash_value = parse_hash(metadata_value)

        # lookup code file
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

        # lookup metadata file
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

    # get existing records
    old_package_code_files = app.data.sql.get_package_code_files(
        repository, package_name
    )
    old_package_metadata_files = app.data.sql.get_package_metadata_files(
        repository, package_name
    )

    # not the best way to do this, but it works
    old_package_code_files_names = set(x.filename for x in old_package_code_files)
    old_package_metadata_files_names = set(
        x.filename for x in old_package_metadata_files
    )

    new_records = [
        n
        for n in new_package_code_files
        if n.filename not in old_package_code_files_names
    ] + [
        n
        for n in new_package_metadata_files
        if n.filename not in old_package_metadata_files_names
    ]

    # commit changes
    app.data.sql.upload_new_package_files(new_records)


def update_package_data(repository: Repository, package_name: str) -> None:
    """
    Update the package data for a given package in our database
    """
    logger.info(f"Updating {log_package_name(repository, package_name)}")

    # parse the simple registry
    parse_simple_registry(repository, package_name)

    # record the last time we've updated this package
    app.data.sql.update_package_last_updated(repository, package_name)


def get_package_code_files(repository_slug: str, package_name: str) -> list[CodeFile]:
    """
    Get a list of PackageCodeFiles objects for a given package
    """
    repository = app.data.sql.lookup_repository(repository_slug)
    if repository is None:
        raise app.models.exceptions.RepositoryNotFound(repository_slug)

    # check last updated time
    package_update = app.data.sql.lookup_package_update(repository, package_name)

    # check if package data is current
    if package_update is None or not package_update.is_current:
        update_package_data(repository, package_name)
    else:
        logger.debug(f"Using cached data for {
                     log_package_name(repository, package_name)}")

    # get package filenames
    return app.data.sql.get_package_code_files(repository, package_name)


def cache_file(package_file: PackageFile) -> None:
    """
    Cache a file
    """
    # skip if already cached
    if package_file.is_cached:
        return

    # upload the main file
    app.data.storage.active.ActiveStorage.provider.cache_file(package_file)

    # update the database
    app.data.sql.mark_as_cached(package_file)


def get_package_file(
    repository_slug: str, package_name: str, filename: str
) -> PackageFile:
    """
    Return a PackageFile object for a given package and filename
    """
    repository = app.data.sql.lookup_repository(repository_slug)
    if repository is None:
        raise app.models.exceptions.RepositoryNotFound(repository_slug)

    # try to find the file in the database
    package_file = app.data.sql.lookup_package_file(repository, filename)

    if not package_file:
        logger.debug(
            f"Package file {filename} not found in {
                log_package_name(repository, package_name)}, refreshing data",
        )
        # refresh the package data
        update_package_data(repository, package_name)

        # try again
        package_file = app.data.sql.lookup_package_file(repository, filename)

        # now fail if still not found
        if not package_file:
            raise app.models.exceptions.PackageFileNotFound(
                repository, package_name, filename
            )

    # if we haven't cached the file yet, do so now
    cache_file(package_file)

    return package_file

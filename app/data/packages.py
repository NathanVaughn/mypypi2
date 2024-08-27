import html
from urllib.parse import urljoin

import lxml.html
import packaging.utils
from loguru import logger

import app.data.proxy
import app.data.sql
import app.data.storage.active
import app.models.exceptions
from app.constants import METDATA_EXTENSION
from app.models.package_code_file import PackageCodeFile
from app.models.package_file import PackageFile
from app.models.package_metadata_file import PackageMetadataFile
from app.models.repository import Repository


def parse_filename_version(filename: str) -> str:
    if filename.endswith(".whl"):
        _, version, _, _ = packaging.utils.parse_wheel_filename(filename)
        version = str(version)
    elif filename.endswith(".tar.gz") or filename.endswith(".zip"):
        _, version = packaging.utils.parse_sdist_filename(filename)
        version = str(version)
    elif filename.endswith(".tar.bz2"):
        # example
        # coverage-4.0a5.tar.bz2
        # lie about file extension
        _, version = packaging.utils.parse_sdist_filename(
            filename.replace(".tar.bz2", ".tar.gz")
        )
        version = str(version)
    elif filename.endswith(".egg"):
        # {distribution_name}-{version}-{python_version}.egg
        # example
        # lxml-2.0-py2.4-win32.egg
        version = filename.split("-")[1]
    elif filename.endswith(".exe") or filename.endswith(".msi"):
        # examples
        # lxml-1.3.4.win32-py2.4.exe
        # lxml-2.2.win32-py2.4.exe
        # greenlet-0.4.4.win-amd64-py2.6.msi
        version = filename.split("-")[1].split(".win")[0]
    elif filename.endswith(".rpm"):
        # example
        # setuptools-0.6c4-1.src.rpm
        version = filename.split("-")[1]
    else:
        raise ValueError(f"Unknown file type: {filename}")

    return version


def parse_sha256_hash(given: str) -> str | None:
    """
    Parse the sha256 hash from a string
    """
    if given.startswith("sha256="):
        return given.split("=")[1]
    return None


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
    new_package_code_files: list[PackageCodeFile] = []
    new_package_metadata_files: list[PackageMetadataFile] = []

    # iterate over all anchor tags
    for anchor_tag in upstream_tree.iter("a"):
        # inner text is filename
        filename = anchor_tag.text

        # parse filename
        version = parse_filename_version(filename)

        # get upstream url and sha256 hash
        href = anchor_tag.attrib["href"]
        absolute_href = urljoin(package_simple_url, href)
        if "#" in absolute_href:
            upstream_url = absolute_href.split("#")[0]
            upstream_sha256_hash = parse_sha256_hash(absolute_href.split("#")[1])
        else:
            upstream_url = absolute_href
            upstream_sha256_hash = None

        # get python requires
        requires_python = html.unescape(
            anchor_tag.attrib.get("data-requires-python", "")
        )

        # grab the sha256 hash from the data-dist-info-metadata attribute
        metadata_sha256_hash = parse_sha256_hash(
            anchor_tag.attrib.get("data-dist-info-metadata", "")
        )

        # lookup code file
        package_code_file = PackageCodeFile(
            repository=repository,
            package_name=package_name,
            version=version,
            filename=filename,
            sha256_hash=upstream_sha256_hash,
            upstream_url=upstream_url,
            requires_python=requires_python,
        )
        new_package_code_files.append(package_code_file)

        # lookup metadata file
        if metadata_sha256_hash:
            metadata_filename = filename + METDATA_EXTENSION
            package_metadata_file = PackageMetadataFile(
                repository=repository,
                package_name=package_name,
                version=version,
                filename=metadata_filename,
                sha256_hash=metadata_sha256_hash,
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
    logger.info(f"Updating {repository.slug}/{package_name}")

    # parse the simple registry
    parse_simple_registry(repository, package_name)

    # record the last time we've updated this package
    app.data.sql.update_package_last_updated(repository, package_name)


def get_package_code_files(
    repository_slug: str, package_name: str
) -> list[PackageCodeFile]:
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
        logger.debug(f"Using cached data for {repository.slug}/{package_name}")

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
    Get a list of PackageCodeFiles objects for a given package
    """
    repository = app.data.sql.lookup_repository(repository_slug)
    if repository is None:
        raise app.models.exceptions.RepositoryNotFound(repository_slug)

    # try to find the file in the database
    package_file = app.data.sql.lookup_package_file(repository, filename)

    if not package_file:
        logger.debug(
            f"Package file {filename} not found in {
                repository.slug}/{package_name}, refreshing data",
        )
        # refresh the package data
        update_package_data(repository, package_name)

        # try again
        package_file = app.data.sql.lookup_package_file(repository, filename)

        # now fail if still not found
        if not package_file:
            raise app.models.exceptions.PackageFileNotFound(
                repository_slug, package_name, filename
            )

    # if we haven't cached the file yet, do so now
    cache_file(package_file)

    return package_file

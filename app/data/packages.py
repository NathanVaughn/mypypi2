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

    new_records: list[PackageFile] = []

    # iterate over all anchor tags
    for anchor_tag in upstream_tree.iter("a"):
        # inner text is filename
        filename = anchor_tag.text

        # parse filename
        if filename.endswith(".whl"):
            _, version, _, _ = packaging.utils.parse_wheel_filename(filename)
        else:
            _, version = packaging.utils.parse_sdist_filename(filename)
        version = str(version)

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
        package_code_file = app.data.sql.lookup_package_code_file(repository, filename)
        if not package_code_file:
            logger.debug(
                f"Adding {repository.slug}/{package_name}/{version}/{filename}"
            )
            package_code_file = PackageCodeFile(
                repository=repository,
                package_name=package_name,
                version=version,
                filename=filename,
                sha256_hash=upstream_sha256_hash,
                upstream_url=upstream_url,
                requires_python=requires_python,
            )
            new_records.append(package_code_file)

        # lookup metadata file
        if metadata_sha256_hash:
            package_metadata_file = app.data.sql.lookup_package_metadata_file(
                repository, filename
            )
            if not package_metadata_file:
                logger.debug(f"Adding {
                             repository.slug}/{package_name}/{version}/{filename + METDATA_EXTENSION}")
                package_metadata_file = PackageMetadataFile(
                    repository=repository,
                    package_name=package_name,
                    version=version,
                    filename=filename + METDATA_EXTENSION,
                    sha256_hash=metadata_sha256_hash,
                    upstream_url=upstream_url + METDATA_EXTENSION,
                    code_file=package_code_file,
                )
                new_records.append(package_metadata_file)

    # commit changes
    app.data.sql.upload_new_package_files(new_records)


def update_package_data(repository: Repository, package: str) -> None:
    """
    Update the package data for a given package in our database
    """
    logger.info(f"Updating {repository.slug}/{package}")

    # parse the simple registry
    parse_simple_registry(repository, package)

    # record the last time we've updated this package
    app.data.sql.update_package_last_updated(repository, package)


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

    # get package version filenames
    return app.data.sql.get_package_code_files(repository, package_name)


def cache_file(package_file: PackageFile) -> None:
    """
    Cache a file
    """
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
    if not package_file.is_cached:
        cache_file(package_file)

    return package_file

import concurrent.futures
from typing import Callable
from urllib.parse import urljoin

import lxml.html
from loguru import logger

import app.data.proxy
import app.data.sql
import app.data.storage.active
from app.models.database import db
from app.models.package_version_filename import PackageVersionFilename


def parse_simple_registry(repository_slug: str, package: str) -> None:
    """
    Parse the simple data from the registry.
    """
    # load metadata from simple endpoint
    repository = app.data.sql.lookup_repository(repository_slug)
    assert repository is not None

    package_simple_url = f"{repository.simple_url}/{package}/"

    # use lxml for performance
    upstream_tree = lxml.html.fromstring(
        app.data.proxy.fetch_url(package_simple_url).contents)
    for anchor_tag in upstream_tree.iter("a"):
        # inner text is filename
        filename = anchor_tag.text

        # get upstream url
        href = anchor_tag.attrib["href"]
        absolute_href = urljoin(package_simple_url, href)
        upstream_url = absolute_href.split("#")[0]

        # lookup entry in the database
        package_version_filename = app.data.sql.lookup_package_version_filename(
            repository_slug, filename)
        if not package_version_filename:
            package_version_filename = PackageVersionFilename(
                repository=repository, package=package, filename=filename
            )

        # grab the sha256 hash from the data-dist-info-metadata attribute
        dist_info_metadata = anchor_tag.attrib.get(
            "data-dist-info-metadata", "")
        if dist_info_metadata.startswith("sha256="):
            package_version_filename.dist_info_metadata_sha256_hash = (
                dist_info_metadata.split("=")[1]
            )

        # grab the sha256 hash from the data-dist-info-metadata attribute
        core_metadata = anchor_tag.attrib.get("data-core-metadata", "")
        if core_metadata.startswith("sha256="):
            package_version_filename.core_metadata_sha256_hash = core_metadata.split(
                "="
            )[1]

    # commit changes
    db.session.commit()


def update_package_data(repository_slug: str, package: str) -> None:
    """
    Update the package data for a given package in our database
    """
    logger.info(f"Updating {package}")

    parse_simple_registry(repository_slug, package)

    # record the last time we've updated this package
    app.data.sql.update_package_last_updated(repository_slug, package)


def get_package_version_filenames(repository_slug: str, package: str) -> list[PackageVersionFilename]:
    """
    Get a list of PackageVersionFilename objects for a given package
    """

    # check last updated time
    package_update = app.data.sql.lookup_package_update(
        repository_slug, package)

    # check if package data is current
    if package_update is None or not package_update.is_current:
        update_package_data(repository_slug, package)

    # get package version filenames
    return app.data.sql.get_package_version_filenames(repository_slug, package)


def cache_file(package_version_filename: PackageVersionFilename) -> None:
    """
    Cache a file
    """
    # keep track of the uploads we need to do
    uploads: list[Callable] = []

    # upload the main file
    uploads.append(
        lambda: app.data.storage.active.ActiveStorage.provider.cache_file(
            package_version_filename
        )
    )

    # also upload the metadata if available
    if (
        package_version_filename.dist_info_metadata_sha256_hash
        or package_version_filename.core_metadata_sha256_hash
    ):
        metadata_url = f"{package_version_filename.upstream_url}.metadata"
        metadata_s3_path = f"{s3_path}.metadata"
        uploads.append(
            lambda: app.data.storage.s3.upload.upload_file(
                s3_options, metadata_url, metadata_s3_path
            )
        )

    # do the uploads
    with concurrent.futures.ThreadPoolExecutor(2) as executor:
        futures = [executor.submit(upload) for upload in uploads]
        # need to wait for the results to actually upload the files
        [future.result() for future in futures]

    # update the database
    package_version_filename.is_cached = True
    db.session.commit()

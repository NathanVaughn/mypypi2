import concurrent.futures
import datetime
from typing import Callable

import lxml.html
import pyjson5
from flask import current_app
from loguru import logger

import app.data.proxy
import app.data.storage.s3.path
import app.data.storage.s3.upload
from app.models.database import db
from app.models.package_update import PackageUpdate
from app.models.package_version_filename import PackageVersionFilename


def lookup_filename(filename: str) -> PackageVersionFilename | None:
    """
    Lookup a PackageVersionFilename object given the filename
    """
    return db.session.execute(
        db.select(PackageVersionFilename).filter_by(filename=filename)
    ).scalar_one_or_none()


def parse_json_registry(package: str) -> None:
    """
    Parse the JSON data from the registry.
    This should always be run before parsing the simple registry.
    """
    # get the JSON data
    upstream = current_app.config["UPSTREAM_JSON_URL_PREFIX"].removesuffix("/")
    url = f"{upstream}/{package}/json"

    # use pyjson5 for performance
    registry_data = pyjson5.decode_buffer(app.data.proxy.fetch_url(url).contents)

    new_records: list[PackageVersionFilename] = []

    # go through each release
    for version in registry_data["releases"].keys():
        for file_data in registry_data["releases"][version]:
            # see if file already exists
            filename = file_data["filename"]
            package_version_filename = lookup_filename(filename)

            # if not, add it
            if not package_version_filename:
                logger.info(f"Adding {package}/{version}/{filename}")
                new_records.append(
                    PackageVersionFilename(
                        package=package,
                        version=version,
                        filename=filename,
                        python_requires=file_data["requires_python"],
                        blake2b_256_hash=file_data["digests"]["blake2b_256"],
                        md5_hash=file_data["digests"]["md5"],
                        sha256_hash=file_data["digests"]["sha256"],
                        upstream_url=file_data["url"],
                    )
                )

    db.session.add_all(new_records)
    db.session.commit()


def parse_simple_registry(package: str) -> None:
    """
    Parse the simple data from the registry.
    This should always be run after parsing the JSON registry.
    """
    # load metadata from simple endpoint
    upstream = current_app.config["UPSTREAM_SIMPLE_URL_PREFIX"].removesuffix("/")
    url = f"{upstream}/{package}"

    # use lxml for performance
    upstream_tree = lxml.html.fromstring(app.data.proxy.fetch_url(url).contents)
    for anchor_tag in upstream_tree.iter("a"):
        # inner text is filename
        filename = anchor_tag.text

        # lookup entry in the database
        package_version_filename = lookup_filename(filename)
        if not package_version_filename:
            # skip if not found
            # this should never happen
            continue

        # grab the sha256 hash from the data-dist-info-metadata attribute
        dist_info_metadata = anchor_tag.attrib.get("data-dist-info-metadata", "")
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


def update_package_data(package: str) -> None:
    """
    Update the package data for a given package in our database
    """
    logger.info(f"Updating {package}")

    parse_json_registry(package)
    parse_simple_registry(package)

    # record the last time we've updated this package
    package_update = db.session.execute(
        db.select(PackageUpdate).filter_by(package=package)
    ).scalar_one_or_none()

    if package_update is None:
        # create a new record if this is the first time
        package_update = PackageUpdate(
            package=package, last_updated=datetime.datetime.now()
        )
        db.session.add(package_update)
    else:
        package_update.last_updated = datetime.datetime.now()

    db.session.commit()


def get_package_version_filenames(package: str) -> list[PackageVersionFilename]:
    """
    Get a list of PackageVersionFilename objects for a given package
    """

    # check last updated time
    package_update: PackageUpdate | None = db.session.execute(
        db.select(PackageUpdate).filter_by(package=package)
    ).scalar_one_or_none()

    # check if package data is current
    if package_update is None or not package_update.is_current:
        update_package_data(package)

    # get package version filenames
    result: list[PackageVersionFilename] = (
        db.session.execute(
            db.select(
                # type: ignore
                PackageVersionFilename
            ).filter_by(package=package)
        )
        .scalars()
        .all()
    )

    return result


def cache_file(package_version_filename: PackageVersionFilename) -> None:
    """
    Cache a file
    """
    # keep track of the uploads we need to do
    uploads: list[Callable] = []

    s3_options = current_app.config.get_namespace("S3_")

    # upload the main file
    s3_path = app.data.storage.s3.path.upload_path(package_version_filename)
    uploads.append(
        lambda: app.data.storage.s3.upload.upload_file(
            s3_options, package_version_filename.upstream_url, s3_path
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

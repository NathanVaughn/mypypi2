import datetime

import pyjson5
import requests
import s3fs
from flask import current_app
from loguru import logger

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


def update_package_data(package: str) -> None:
    """
    Update the package data for a given package in our database
    """
    logger.info(f"Updating {package}")

    # TODO get metadata hash

    # update stored package data
    upstream = current_app.config["UPSTREAM_JSON_URL_PREFIX"].removesuffix("/")
    url = f"{upstream}/{package}/json"
    # use pyjson5 for performance
    upstream_data = pyjson5.decode_buffer(requests.get(url).content)

    # keep track of new additions for batch query
    new_obj = []

    # go through each release
    for version in upstream_data["releases"].keys():
        for file_data in upstream_data["releases"][version]:
            # see if file already exists
            filename = file_data["filename"]
            package_version_filename = lookup_filename(filename)

            # if not, add it
            if not package_version_filename:
                logger.info(f"Adding {package}/{version}/{filename}")
                new_obj.append(
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

    # record the last time we've updated this package
    new_obj.append(PackageUpdate(package=package, last_updated=datetime.datetime.now()))

    db.session.add_all(new_obj)
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
    logger.info(f"Caching {package_version_filename}")

    # setup the s3 connection first
    s3 = s3fs.S3FileSystem(
        endpoint_url=current_app.config["S3_ENDPOINT_URL"],
        key=current_app.config["S3_ACCESS_KEY_ID"],
        secret=current_app.config["S3_SECRET_ACCESS_KEY"],
        client_kwargs={"region_name": current_app.config["S3_REGION_NAME"]},
    )

    # build the s3 path
    s3_bucket_prefix = current_app.config["S3_BUCKET_PREFIX"].removesuffix("/")
    s3_path = f"{current_app.config['S3_BUCKET_NAME']}/{s3_bucket_prefix}/{package_version_filename.package}/{
        package_version_filename.version}/{package_version_filename.filename}"

    # stream the file to S3
    logger.info(f"Uploading {package_version_filename.upstream_url} to {s3_path}")
    with s3.open(s3_path, "wb") as fp:
        with requests.get(
            package_version_filename.upstream_url, stream=True
        ) as response:
            for chunk in response.iter_content(chunk_size=8192):
                fp.write(chunk)

    # also stream the metadata if available
    if package_version_filename.metadata_sha256_hash:
        metadata_url = f"{package_version_filename.upstream_url}.metadata"
        metadata_s3_path = f"{s3_path}.metadata"
        logger.info(f"Uploading {metadata_url} to {metadata_s3_path}")
        with s3.open(metadata_s3_path, "wb") as fp:
            with requests.get(metadata_url, stream=True) as response:
                for chunk in response.iter_content(chunk_size=8192):
                    fp.write(chunk)

    # update the database
    package_version_filename.is_cached = True
    db.session.commit()

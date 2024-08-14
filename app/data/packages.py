import datetime

import pyjson5
import requests
from loguru import logger

from app.constants import UPDATE_INTERVAL, UPSTREAM_JSON_PREFIX
from app.models.database import db
from app.models.package_update import PackageUpdate
from app.models.package_version_filename import PackageVersionFilename


def update_package_data(package: str) -> None:
    logger.info(f"Updating {package}")

    # update stored package data
    url = f"{UPSTREAM_JSON_PREFIX}/{package}/json"
    # use pyjson5 for performance
    upstream_data = pyjson5.decode_buffer(requests.get(url).content)

    # keep track of new additions for batch query
    new_obj = []

    # go through each release
    for version in upstream_data["releases"].keys():
        for file_data in upstream_data["releases"][version]:
            # see if file already exists
            filename = file_data["filename"]
            package_version_filename: PackageVersionFilename | None = (
                db.session.execute(
                    db.select(PackageVersionFilename).filter_by(
                        filename=file_data["filename"]
                    )
                ).scalar_one_or_none()
            )
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

    new_obj.append(PackageUpdate(package=package, last_updated=datetime.datetime.now()))

    db.session.add_all(new_obj)
    db.session.commit()


def get_package_version_filenames(package: str) -> list[PackageVersionFilename]:
    # check last updated time
    package_update: PackageUpdate | None = db.session.execute(
        db.select(PackageUpdate).filter_by(package=package)
    ).scalar_one_or_none()

    if (
        package_update is None
        or package_update.last_updated < datetime.datetime.now() - UPDATE_INTERVAL
    ):
        # update package
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

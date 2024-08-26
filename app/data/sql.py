import datetime
from typing import Sequence

from app.constants import METDATA_EXTENSION
from app.models.database import db
from app.models.package_code_file import PackageCodeFile
from app.models.package_file import PackageFile
from app.models.package_metadata_file import PackageMetadataFile
from app.models.package_update import PackageUpdate
from app.models.repository import Repository
from app.models.url_cache import URLCache


def lookup_repository(repository_slug: str) -> Repository | None:
    """
    Lookup a Repository object given the slug
    """
    return db.session.execute(
        db.select(Repository).where(Repository.slug == repository_slug)
    ).scalar_one_or_none()


def lookup_package_file(repository: Repository, filename: str) -> PackageFile | None:
    if filename.endswith(METDATA_EXTENSION):
        return lookup_package_metadata_file(repository, filename)
    return lookup_package_code_file(repository, filename)


def lookup_package_code_file(
    repository: Repository, filename: str
) -> PackageCodeFile | None:
    """
    Lookup a PackageCodeFile object given the filename
    """
    return db.session.execute(
        db.select(PackageCodeFile)
        .join(PackageCodeFile.repository)
        .where(
            PackageCodeFile.filename == filename,
            Repository.id == repository.id,
        )
    ).scalar_one_or_none()


def lookup_package_metadata_file(
    repository: Repository, filename: str
) -> PackageMetadataFile | None:
    """
    Lookup a PackageMetadataFile object given the filename
    """
    return db.session.execute(
        db.select(PackageMetadataFile)
        .join(PackageMetadataFile.repository)
        .where(
            PackageMetadataFile.filename == filename,
            Repository.id == repository.id,
        )
    ).scalar_one_or_none()


def lookup_package_update(
    repository: Repository, package_name: str
) -> PackageUpdate | None:
    """
    Lookup a PackageUpdate object given the package name
    """
    return db.session.execute(
        db.select(PackageUpdate)
        .join(PackageUpdate.repository)
        .where(
            PackageUpdate.package_name == package_name, Repository.id == repository.id
        )
    ).scalar_one_or_none()


def lookup_url_cache(repository: Repository, url: str) -> URLCache | None:
    """
    Lookup a URLCache object given the url
    """
    return db.session.execute(
        db.select(URLCache)
        .join(URLCache.repository)
        .where(URLCache.url == url, Repository.id == repository.id)
    ).scalar_one_or_none()


def get_package_metadata_files(
    repository: Repository, package_name: str
) -> list[PackageMetadataFile]:
    """
    Return a list of PackageMetadataFile objects for a given package
    """
    return (
        db.session.execute(
            db.select(PackageMetadataFile)
            .join(PackageMetadataFile.repository)
            .where(
                PackageMetadataFile.package_name == package_name,
                Repository.id == repository.id,
            )
        )
        .scalars()
        .all()
    )  # type: ignore


def get_package_code_files(
    repository: Repository, package_name: str
) -> list[PackageCodeFile]:
    """
    Return a list of PackageCodeFile objects for a given package
    """
    return (
        db.session.execute(
            db.select(PackageCodeFile)
            .join(PackageCodeFile.repository)
            .where(
                PackageCodeFile.package_name == package_name,
                Repository.id == repository.id,
            )
        )
        .scalars()
        .all()
    )  # type: ignore


def update_package_last_updated(repository: Repository, package_name: str) -> None:
    """
    Update the package data for a given package in our database
    """
    # record the last time we've updated this package
    package_update = db.session.execute(
        db.select(PackageUpdate)
        .join(PackageUpdate.repository)
        .where(
            PackageUpdate.package_name == package_name, Repository.id == repository.id
        )
    ).scalar_one_or_none()

    if package_update is None:
        # create a new record if this is the first time
        package_update = PackageUpdate(
            repository=repository,
            package_name=package_name,
            last_updated=datetime.datetime.now(),
        )
        db.session.add(package_update)
    else:
        package_update.last_updated = datetime.datetime.now()

    db.session.commit()


def mark_as_cached(package_file: PackageFile) -> None:
    """
    Mark a package file as cached
    """
    package_file.is_cached = True
    db.session.commit()


def upload_new_package_files(package_files: Sequence[PackageFile]) -> None:
    """
    Upload a new package file
    """
    db.session.add_all(package_files)
    db.session.commit()

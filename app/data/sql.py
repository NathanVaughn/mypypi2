import functools

from app.constants import METADATA_EXTENSION, MINUTES_TO_SECONDS
from app.models.code_file import CodeFile
from app.models.database import db
from app.models.exceptions import (
    PackageFileNotFound,
    PackageNotFound,
    RepositoryNotFound,
)
from app.models.metadata_file import MetadataFile
from app.models.package import Package
from app.models.package_file import PackageFile
from app.models.repository import Repository


def save() -> None:
    """
    Save changes made to existing objects.
    """
    db.session.commit()


def get_repository(repository_slug: str) -> Repository | None:
    """
    Lookup a Repository object given the slug.
    Returns None if not found.
    """
    return db.session.execute(db.select(Repository).where(Repository.slug == repository_slug)).scalar_one_or_none()


def get_repository_with_exception(repository_slug: str) -> Repository:
    """
    Lookup a Repository object given the slug.
    Raises an exception if not found.
    """
    repository = get_repository(repository_slug)
    if repository is None:
        raise RepositoryNotFound(repository_slug)
    return repository


@functools.cache
def get_repository_timeout(repository_slug: str) -> int:
    """
    Lookup a Repository timeout in seconds.
    """
    # only use memory cache.
    # Because we're returning an integer, can cache this fine
    # the page level caching uses this

    repository = get_repository_with_exception(repository_slug)
    return repository.cache_minutes * MINUTES_TO_SECONDS


def get_package(repository: Repository, package_name: str) -> Package | None:
    """
    Lookup a Package object given the Repository and package name.
    Returns None if not found.
    """
    return db.session.execute(db.select(Package).where(Package.repository_id == repository.id, Package.name == package_name)).scalar_one_or_none()


def get_package_with_exception(repository: Repository, package_name: str) -> Package:
    """
    Lookup a Package object given the Repository and package name.
    Raises an exception if not found.
    """
    package = get_package(repository=repository, package_name=package_name)
    if package is None:
        raise PackageNotFound(repository_slug=repository.slug, package_name=package_name)
    return package


def get_metadata_file(repository: Repository, package: Package, filename: str) -> MetadataFile | None:
    """
    Lookup a MetadataFile object given the Repository, Package, and filename.
    """
    return db.session.execute(
        db.select(MetadataFile).where(
            MetadataFile.package.repository.id == repository.id,
            MetadataFile.package.id == package.id,
            MetadataFile.filename == filename,
        )
    ).scalar_one_or_none()


def get_code_file(repository: Repository, package: Package, filename: str) -> CodeFile | None:
    """
    Lookup a MetadataFile object given the Repository, Package, and filename.
    """
    return db.session.execute(
        db.select(CodeFile).where(
            CodeFile.package.repository.id == repository.id,
            CodeFile.package.id == package.id,
            CodeFile.filename == filename,
        )
    ).scalar_one_or_none()


def get_package_file_with_exception(repository: Repository, package: Package, filename: str) -> PackageFile:
    """
    Lookup a PackageFile object given the Repository, Package, and filename.
    Raises an exception if not found.
    """
    if filename.endswith(METADATA_EXTENSION):
        package_file = get_metadata_file(repository, package, filename)
    else:
        package_file = get_code_file(repository, package, filename)

    if package_file is None:
        raise PackageFileNotFound(repository, package.name, filename)

    return package_file


def save_package(package: Package) -> None:
    """
    Save a new Package object.
    """
    db.session.add(package)
    save()

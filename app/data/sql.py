import functools

from app.constants import METADATA_EXTENSION, MINUTES_TO_SECONDS
from app.models.code_file import CodeFile
from app.models.code_file_hash import CodeFileHash
from app.models.database import db
from app.models.exceptions import (
    PackageFileNotFound,
    PackageNotFound,
    RepositoryNotFound,
)
from app.models.metadata_file import MetadataFile
from app.models.metadata_file_hash import MetadataFileHash
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
    return (
        db.session.execute(
            db.select(MetadataFile)
            .join(MetadataFile.package)
            .join(Package.repository)
            .where(
                Repository.id == repository.id,
                Package.id == package.id,
                MetadataFile.filename == filename,
            )
        )
        .unique()
        .scalar_one_or_none()
    )


def get_code_file(repository: Repository, package: Package, filename: str) -> CodeFile | None:
    """
    Lookup a MetadataFile object given the Repository, Package, and filename.
    """
    return (
        db.session.execute(
            db.select(CodeFile)
            .join(CodeFile.package)
            .join(Package.repository)
            .where(
                Repository.id == repository.id,
                Package.id == package.id,
                CodeFile.filename == filename,
            )
        )
        .unique()
        .scalar_one_or_none()
    )


def get_package_file_with_exception(repository: Repository, package: Package, filename: str) -> PackageFile:
    """
    Lookup a PackageFile object given the Repository, Package, and filename.
    Raises an exception if not found.
    """
    if filename.endswith(METADATA_EXTENSION):
        package_file = get_metadata_file(repository=repository, package=package, filename=filename)
    else:
        package_file = get_code_file(repository=repository, package=package, filename=filename)

    if package_file is None:
        raise PackageFileNotFound(package=package, filename=filename)

    return package_file


# def save_package(package: Package) -> None:
#     db.session.add(package)
#     # add the package so we can get the id
#     save()


def save_package(package: Package) -> None:
    """
    Save a new Package object.
    """
    # while this is faster than a naive `db.session.add(package)`, db.session.commit()`,
    # it's really not that signficant.

    # what this does is carefully detach and reattach child models
    # so we can bulk insert one table at a time.

    # sqlalchemy ORM mode will not bulk insert ORM records, much less with foreign keys
    # so this is a bit more manual, by bulk inserting one table at a time, getting the
    # generated IDs, and then inserting the next child table.

    code_files = package.code_files
    package.code_files = []
    db.session.add(package)
    # add the package so we can get the id
    save()

    # now reattch code files, but break links to hashes and metadata files
    code_file_hashes: dict[CodeFile, list[CodeFileHash]] = {}
    code_file_metdata_file: dict[CodeFile, MetadataFile] = {}
    metadata_file_hashes: dict[MetadataFile, list[MetadataFileHash]] = {}
    for code_file in code_files:
        # break hashes
        code_file_hashes[code_file] = code_file.hashes
        code_file.hashes = []
        # break metadata file
        if code_file.metadata_file:
            # break metadata file hashes
            metadata_file_hashes[code_file.metadata_file] = code_file.metadata_file.hashes
            code_file.metadata_file.hashes = []

            # break metadata file
            code_file_metdata_file[code_file] = code_file.metadata_file
            code_file.metadata_file = None

        # reattach package
        code_file.package_id = package.id

    # now bulk insert the code files
    code_file_ids = db.session.scalars(db.insert(CodeFile).returning(CodeFile.id), [code_file.to_dict() for code_file in code_files]).all()

    # reattach the code file ids
    for code_file, code_file_id in zip(code_files, code_file_ids):
        code_file.id = code_file_id

    # reattach hashes
    for code_file, hashes in code_file_hashes.items():
        for hash in hashes:
            hash.code_file_id = code_file.id

    # bulk insert hashes
    db.session.execute(db.insert(CodeFileHash).values([hash.to_dict() for hashes in code_file_hashes.values() for hash in hashes]))

    # reattach metadata files
    for code_file, metadata_file in code_file_metdata_file.items():
        metadata_file.package_id = package.id
        metadata_file.code_file_id = code_file.id

    # bulk insert metadata files
    metadata_file_ids = db.session.scalars(db.insert(MetadataFile).returning(MetadataFile.id), [metadata_file.to_dict() for metadata_file in code_file_metdata_file.values()]).all()

    # reattach the metadata file ids
    for metadata_file, metadata_file_id in zip(code_file_metdata_file.values(), metadata_file_ids):
        metadata_file.id = metadata_file_id

    # reattach metadata file hashes
    for metadata_file, hashes in metadata_file_hashes.items():
        for hash in hashes:
            hash.metadata_file_id = metadata_file.id

    # bulk insert metadata file hashes
    db.session.execute(db.insert(MetadataFileHash).values([hash.to_dict() for hashes in metadata_file_hashes.values() for hash in hashes]))

    save()

import functools

from app.constants import METADATA_EXTENSION, MINUTES_TO_SECONDS
from app.data.sql.main2 import convert_sql_to_pydantic
from app.models.code_file import CodeFile, CodeFileSQL
from app.models.code_file_hash import CodeFileHash, CodeFileHashSQL
from app.models.database import db
from app.models.exceptions import (
    PackageFileNotFound,
    PackageNotFound,
    RepositoryNotFound,
)
from app.models.metadata_file import MetadataFile, MetadataFileSQL
from app.models.metadata_file_hash import MetadataFileHash, MetadataFileHashSQL
from app.models.package import Package, PackageSQL
from app.models.package_file import PackageFile
from app.models.repository import Repository, RepositorySQL


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
    repository: RepositorySQL | None = db.session.execute(db.select(
        RepositorySQL).where(RepositorySQL.slug == repository_slug)).scalar_one_or_none()
    if repository is not None:
        return convert_sql_to_pydantic(repository)


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
    package: PackageSQL | None = db.session.execute(db.select(PackageSQL).where(
        PackageSQL.repository_id == repository.id, PackageSQL.name == package_name)).scalar_one_or_none()
    if package is not None:
        return convert_sql_to_pydantic(package)


def get_package_with_exception(repository: Repository, package_name: str) -> Package:
    """
    Lookup a Package object given the Repository and package name.
    Raises an exception if not found.
    """
    package = get_package(repository=repository, package_name=package_name)
    if package is None:
        raise PackageNotFound(
            repository_slug=repository.slug, package_name=package_name)
    return package


def get_metadata_file(repository: Repository, package: Package, filename: str) -> MetadataFile | None:
    """
    Lookup a MetadataFile object given the Repository, Package, and filename.
    """
    metadata_file: MetadataFileSQL | None = (
        db.session.execute(
            db.select(MetadataFileSQL)
            .join(MetadataFileSQL.package)
            .join(PackageSQL.repository)
            .where(
                RepositorySQL.id == repository.id,
                PackageSQL.id == package.id,
                MetadataFileSQL.filename == filename,
            )
        )
        .unique()
        .scalar_one_or_none()
    )
    if metadata_file is not None:
        return convert_sql_to_pydantic(metadata_file)


def get_code_file(repository: Repository, package: Package, filename: str) -> CodeFile | None:
    """
    Lookup a MetadataFile object given the Repository, Package, and filename.
    """
    code_file: CodeFileSQL | None = (
        db.session.execute(
            db.select(CodeFileSQL)
            .join(CodeFileSQL.package)
            .join(PackageSQL.repository)
            .where(
                RepositorySQL.id == repository.id,
                PackageSQL.id == package.id,
                CodeFileSQL.filename == filename,
            )
        )
        .unique()
        .scalar_one_or_none()
    )
    if code_file is not None:
        return convert_sql_to_pydantic(code_file)


def get_package_file_with_exception(repository: Repository, package: Package, filename: str) -> PackageFile:
    """
    Lookup a PackageFile object given the Repository, Package, and filename.
    Raises an exception if not found.
    """
    if filename.endswith(METADATA_EXTENSION):
        package_file = get_metadata_file(
            repository=repository, package=package, filename=filename)
    else:
        package_file = get_code_file(
            repository=repository, package=package, filename=filename)

    if package_file is None:
        raise PackageFileNotFound(package=package, filename=filename)

    return package_file


def save_package(package: Package) -> None:
    package_id = db.session.scalars(db.insert(PackageSQL).returning(
        PackageSQL.id), [package.model_dump()]).first()

    code_files = package.code_files
    for code_file in code_files:
        code_file.package_id = package_id

    # now bulk insert the code files
    code_file_ids = db.session.scalars(db.insert(CodeFileSQL).returning(
        CodeFileSQL.id), [code_file.model_dump() for code_file in code_files]).all()

    code_file_hashes: list[CodeFileHash] = []
    metadata_files: list[MetadataFile] = []

    # reattach the code file ids
    for code_file, code_file_id in zip(code_files, code_file_ids):
        code_file.id = code_file_id
        # update the code file hashes to get the parent ID
        for hash in code_file.hashes:
            hash.code_file_id = code_file_id
            code_file_hashes.append(hash)
        # update the metadata file to get the parent ID as well
        if code_file.metadata_file:
            code_file.metadata_file.package_id = package_id
            code_file.metadata_file.code_file_id = code_file_id
            metadata_files.append(code_file.metadata_file)

    # bulk insert code file hashes
    db.session.execute(db.insert(CodeFileHashSQL).values(
        [hash.model_dump() for hash in code_file_hashes]))

    # bulk insert metadata files
    metadata_file_ids = db.session.scalars(db.insert(MetadataFileSQL).returning(
        MetadataFileSQL.id), [metadata_file.model_dump() for metadata_file in metadata_files]).all()

    # reattach the metadata file ids
    metadata_file_hashes: list[MetadataFileHash] = []
    for metadata_file, metadata_file_id in zip(metadata_files, metadata_file_ids):
        metadata_file.id = metadata_file_id
        for hash in metadata_file.hashes:
            hash.metadata_file_id = metadata_file_id
            metadata_file_hashes.append(hash)

    # bulk insert metadata file hashes
    db.session.execute(db.insert(MetadataFileHashSQL).values(
        [hash.model_dump() for hash in metadata_file_hashes]))

    save()

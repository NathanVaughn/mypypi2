
from __future__ import annotations

from typing import TYPE_CHECKING, Type, overload

from app.models.database import db

if TYPE_CHECKING:
    from app.models.code_file import CodeFile, CodeFileSQL
    from app.models.metadata_file import MetadataFile, MetadataFileSQL
    from app.models.package import Package, PackageSQL
    from app.models.repository import Repository, RepositorySQL


@overload
def convert_sql_to_pydantic(sql_object: RepositorySQL) -> Repository: ...


@overload
def convert_sql_to_pydantic(sql_object: PackageSQL) -> Package: ...


@overload
def convert_sql_to_pydantic(sql_object: CodeFileSQL) -> CodeFile: ...


@overload
def convert_sql_to_pydantic(sql_object: MetadataFileSQL) -> MetadataFile: ...


def convert_sql_to_pydantic(sql_object: RepositorySQL | PackageSQL | CodeFileSQL | MetadataFileSQL) -> Repository | Package | CodeFile | MetadataFile:
    """
    Convert a SQLAlchemy object to a Pydantic object.
    """
    from app.models.code_file import CodeFile, CodeFileSQL
    from app.models.code_file_hash import CodeFileHash, CodeFileHashSQL
    from app.models.metadata_file import MetadataFile, MetadataFileSQL
    from app.models.metadata_file_hash import MetadataFileHash, MetadataFileHashSQL
    from app.models.package import Package, PackageSQL
    from app.models.repository import Repository, RepositorySQL

    SQL_TO_PYDANTIC_TABLE = {
        RepositorySQL: Repository,
        PackageSQL: Package,
        CodeFileSQL: CodeFile,
        MetadataFileSQL: MetadataFile,
        CodeFileHashSQL: CodeFileHash,
        MetadataFileHashSQL: MetadataFileHash,
    }

    PYDANTIC_TO_SQL_TABLE = {
        Repository: RepositorySQL,
        Package: PackageSQL,
        CodeFile: CodeFileSQL,
        MetadataFile: MetadataFileSQL,
        CodeFileHash: CodeFileHashSQL,
        MetadataFileHash: MetadataFileHashSQL,
    }

    return SQL_TO_PYDANTIC_TABLE[type(sql_object)].model_validate(sql_object, from_attributes=True)


@overload
def get_by_id(sql_object: Type[RepositorySQL], id: int) -> Repository: ...


@overload
def get_by_id(sql_object: Type[PackageSQL], id: int) -> Package: ...


@overload
def get_by_id(sql_object: Type[CodeFileSQL], id: int) -> CodeFile: ...


@overload
def get_by_id(sql_object: Type[MetadataFileSQL],
              id: int) -> MetadataFile: ...


def get_by_id(sql_object: Type[RepositorySQL] | Type[PackageSQL] | Type[CodeFileSQL] | Type[MetadataFileSQL], id: int) -> Repository | Package | CodeFile | MetadataFile:
    """
    Convert a SQLAlchemy object to a Pydantic object.
    """
    result = db.session.execute(db.select(sql_object).where(
        sql_object.id == id)).scalar_one_or_none()
    if result is None:
        raise ValueError(f"Object with ID {id} not found")
    return convert_sql_to_pydantic(result)

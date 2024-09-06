from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.package_file_hash import PackageFileHash

if TYPE_CHECKING:
    from app.models.code_file import CodeFile  # pragma: no cover


class CodeFileHash(PackageFileHash, table=True):
    """
    This model represents a content hash for a code file associated with a package.
    As there cannot be a foreign key to two different tables, this exists
    as a seperate table.
    """

    code_file_id: str = Field(foreign_key="code_file.id")
    code_file: "CodeFile" = Relationship(
        back_populates="hashes", sa_relationship_kwargs={"lazy": "joined"})

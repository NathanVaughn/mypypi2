from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.package_file_hash import PackageFileHash

if TYPE_CHECKING:
    from app.models.metadata_file import MetadataFile  # pragma: no cover


class MetadataFileHash(PackageFileHash, table=True):
    """
    This model represents a content hash for a metdata file associated with a package.
    As there cannot be a foreign key to two different tables, this exists
    as a seperate table.
    """

    metadata_file_id: str = Field(foreign_key="metadata_file.id")
    metadata_file: "MetadataFile" = Relationship(
        back_populates="hashes", sa_relationship_kwargs={"lazy": "joined"})

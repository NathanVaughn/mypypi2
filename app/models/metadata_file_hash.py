from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file_hash import PackageFileHash, PackageFileHashSQL

if TYPE_CHECKING:
    from app.models.metadata_file import (
        MetadataFileSQL,  # pragma: no cover
    )


class MetadataFileHashSQL(PackageFileHashSQL):
    """
    This model represents a content hash for a metdata file associated with a package.
    As there cannot be a foreign key to two different tables, this exists
    as a seperate table.
    """

    __tablename__ = "metadata_file_hash"
    __table_args__ = (UniqueConstraint("kind", "metadata_file_id", name="_kind_metadata_file_id_id_uc"),)

    metadata_file_id: Mapped[int] = mapped_column(ForeignKey("metadata_file.id"), nullable=True)
    metadata_file: Mapped[MetadataFileSQL] = relationship("MetadataFileSQL", lazy="joined", back_populates="hashes")


class MetadataFileHash(PackageFileHash):
    """
    Pydantic model for MetadataFileHashSQL
    """

    # metadata_file: "MetadataFile" = Field(exclude=True)  # forward reference
    metadata_file_id: int | None = None  # comes from SQL model

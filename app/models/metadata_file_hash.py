from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file_hash import PackageFileHash

if TYPE_CHECKING:
    from app.models.metadata_file import MetadataFile  # pragma: no cover


class MetadataFileHash(PackageFileHash):
    """
    This model represents a content hash for a metdata file associated with a package.
    As there cannot be a foreign key to two different tables, this exists
    as a seperate table.
    """

    __tablename__ = "metadata_file_hash"
    __table_args__ = (UniqueConstraint("kind", "metadata_file_id"),)

    metadata_file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("metadata_file.id"), nullable=True)
    metadata_file: Mapped[MetadataFile] = relationship("MetadataFile", lazy="joined", back_populates="hashes")

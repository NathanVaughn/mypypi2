from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
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
    __table_args__ = (
        ForeignKeyConstraint(["metadata_file_package_id", "metadata_file_filename"], [
                             "metadata_file.package_id", "metadata_file.filename"]),
        UniqueConstraint("kind", "metadata_file_package_id",
                         "metadata_file_filename", name="metadata_file_hash_uc"),
    )

    metadata_file_package_id: Mapped[int] = mapped_column(
        ForeignKey("metadata_file.package_id"))
    metadata_file_filename: Mapped[int] = mapped_column(
        ForeignKey("metadata_file.filename"))
    metadata_file: Mapped[MetadataFile] = relationship(
        "MetadataFile", back_populates="metadata_file", lazy="joined")

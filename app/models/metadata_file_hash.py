from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file_hash import PackageFileHash

if TYPE_CHECKING:
    from app.models.metadata_file import MetadataFile


class MetadataFileHash(PackageFileHash):
    __tablename__ = "metadata_file_hash"
    __table_args__ = (
        UniqueConstraint(
            "kind", "metadata_file_id", name="_kind_metadata_file_id_id_uc"
        ),
    )

    metadata_file_id: Mapped[int] = mapped_column(
        ForeignKey("metadata_file.id"), nullable=True
    )
    metadata_file: Mapped[MetadataFile] = relationship(
        "MetadataFile", lazy="joined", back_populates="hashes"
    )

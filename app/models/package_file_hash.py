from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.package_file import PackageFile  # pragma: no cover


class PackageFileHash(Base):
    __table_args__ = (
        UniqueConstraint("kind", "package_file_id", name="_kind_package_file_id_uc"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """
    Unique identifier
    """

    package_file_id: Mapped[int] = mapped_column(ForeignKey("package_file.id"))
    package_file: Mapped[PackageFile] = relationship(
        "PackageFile", lazy="joined", back_populates="hashes"
    )
    """
    The parent package file
    """

    kind: Mapped[str] = mapped_column(String)
    """
    Type of hash of the file
    """
    value: Mapped[str] = mapped_column(String)
    """
    Hash of the file
    """

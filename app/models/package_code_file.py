from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.package_metadata_file import PackageMetadataFile


class PackageCodeFile(PackageFile):
    __tablename__ = "package_code_file"

    requires_python: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    """
    Python version requirements
    """

    metadata_file: Mapped[PackageMetadataFile] = relationship(
        "PackageMetadataFile", back_populates="code_file"
    )

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.package_code_file import PackageCodeFile


class PackageMetadataFile(PackageFile):
    __tablename__ = "package_metadata_file"

    code_file_id: Mapped[int] = mapped_column(ForeignKey("package_code_file.id"))
    code_file: Mapped[PackageCodeFile] = relationship(
        "PackageCodeFile", back_populates="metadata_file"
    )

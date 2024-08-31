from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.code_file import CodeFile


class MetadataFile(PackageFile):
    __tablename__ = "metadata_file"

    code_file_id: Mapped[int] = mapped_column(ForeignKey("code_file.id"))
    code_file: Mapped[CodeFile] = relationship(
        "CodeFile", back_populates="metadata_file", lazy="joined"
    )

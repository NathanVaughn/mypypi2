from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file_hash import PackageFileHash

if TYPE_CHECKING:
    from app.models.code_file import CodeFile


class CodeFileHash(PackageFileHash):
    __tablename__ = "code_file_hash"
    __table_args__ = (
        UniqueConstraint("kind", "code_file_id", name="_kind_code_file_id_id_uc"),
    )

    code_file_id: Mapped[int] = mapped_column(ForeignKey("code_file.id"), nullable=True)
    code_file: Mapped[CodeFile] = relationship(
        "CodeFile", lazy="joined", back_populates="hashes"
    )

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file_hash import PackageFileHash, PackageFileHashSQL

if TYPE_CHECKING:
    from app.models.code_file import CodeFileSQL  # pragma: no cover


class CodeFileHashSQL(PackageFileHashSQL):
    """
    This model represents a content hash for a code file associated with a package.
    As there cannot be a foreign key to two different tables, this exists
    as a seperate table.
    """

    __tablename__ = "code_file_hash"
    __table_args__ = (UniqueConstraint("kind", "code_file_id", name="_kind_code_file_id_id_uc"),)

    code_file_id: Mapped[int] = mapped_column(ForeignKey("code_file.id"), nullable=True)
    code_file: Mapped[CodeFileSQL] = relationship("CodeFileSQL", lazy="joined", back_populates="hashes")


class CodeFileHash(PackageFileHash):
    """
    Pydantic model for CodeFileHashSQL
    """

    # code_file: "CodeFile" = Field(exclude=True)  # forward reference
    code_file_id: int | None = None  # comes from SQL model

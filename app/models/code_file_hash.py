from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file_hash import PackageFileHash

if TYPE_CHECKING:
    from app.models.code_file import CodeFile  # pragma: no cover


class CodeFileHash(PackageFileHash):
    """
    This model represents a content hash for a code file associated with a package.
    As there cannot be a foreign key to two different tables, this exists
    as a seperate table.
    """

    __tablename__ = "code_file_hash"
    __table_args__ = (ForeignKeyConstraint(["code_file_package_id", "code_file_filename"], [
                      "code_file.package_id", "code_file.filename"]), UniqueConstraint("kind", "code_file_package_id", "code_file_filename", name="code_file_hash_uc"))

    code_file_package_id: Mapped[int] = mapped_column(
        ForeignKey("code_file.package_id"))
    code_file_filename: Mapped[int] = mapped_column(
        ForeignKey("code_file.filename"))
    code_file: Mapped[CodeFile] = relationship(
        "CodeFile", back_populates="metadata_file", lazy="joined")

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.metadata_file import MetadataFile  # pragma: no cover


class CodeFile(PackageFile):
    __tablename__ = "code_file"

    requires_python: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    """
    Python version requirements
    """
    yanked: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    """
    Yanked string. We always show yanked files, but we keep the value here.
    """
    version: Mapped[str] = mapped_column(String, nullable=True, default=None)
    """
    For some files, record the version
    """
    # setting lazy=joined here will ensure that the data for the
    # metadata file is always returned when this is queried
    # This is a huge performance boost when rendering templates
    # with lots of files. Without this, every single record
    # with a metadata file would result in a seperate query.
    metadata_file: Mapped[MetadataFile] = relationship(
        "MetadataFile", back_populates="code_file", lazy="joined"
    )

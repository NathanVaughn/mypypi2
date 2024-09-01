from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.code_file_hash import CodeFileHash  # pragma: no cover
    from app.models.metadata_file import MetadataFile  # pragma: no cover


class CodeFile(PackageFile):
    """
    This model represents a code file associated with a package.
    This is what actually appears in the list of files for a package.
    """

    __tablename__ = "code_file"

    requires_python: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    """
    Python version requirements
    """
    is_yanked: Mapped[bool] = mapped_column(Boolean, default=False)
    yanked_reason: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    """
    Yanked string. We always show yanked files, but we keep the value here.
    """
    # setting lazy=joined here will ensure that the data for the
    # metadata file is always returned when this is queried
    # This is a huge performance boost when rendering templates
    # with lots of files. Without this, every single record
    # with a metadata file would result in a seperate query.
    metadata_file: Mapped[MetadataFile] = relationship("MetadataFile", back_populates="code_file", lazy="joined")

    @declared_attr
    def hashes(cls) -> Mapped[list[CodeFileHash]]:
        """
        A list of hashes for this file
        """
        return relationship("CodeFileHash", back_populates="code_file", lazy="joined")

    # utility properties
    @property
    def yanked(self) -> bool | str:
        """
        Return a boolean if the file is yanked.
        Return a string if the file is yanked with a reason.
        """
        y = self.is_yanked
        if y and self.yanked_reason:
            return self.yanked_reason
        return y

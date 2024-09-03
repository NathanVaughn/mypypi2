from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from pydantic import Field
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file import PackageFile, PackageFileSQL

if TYPE_CHECKING:
    from app.models.code_file_hash import (
        CodeFileHash,  # pragma: no cover
        CodeFileHashSQL,  # pragma: no cover
    )
    from app.models.metadata_file import (
        MetadataFile,  # pragma: no cover
        MetadataFileSQL,  # pragma: no cover
    )


class CodeFileSQL(PackageFileSQL):
    """
    This model represents a code file associated with a package.
    This is what actually appears in the list of files for a package.
    """

    __tablename__ = "code_file"

    requires_python: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None)
    """
    Python version requirements
    """
    is_yanked: Mapped[bool] = mapped_column(Boolean, default=False)
    yanked_reason: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None)
    """
    Yanked string. We always show yanked files, but we keep the value here.
    """
    size: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None)
    """
    File size in bytes
    """
    upload_time: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True, default=None)
    """
    Upload time of the file
    """
    # setting lazy=joined here will ensure that the data for the
    # metadata file is always returned when this is queried
    # This is a huge performance boost when rendering templates
    # with lots of files. Without this, every single record
    # with a metadata file would result in a seperate query.
    metadata_file: Mapped[MetadataFileSQL | None] = relationship(
        "MetadataFileSQL", back_populates="code_file", lazy="joined")

    @declared_attr
    def hashes(cls) -> Mapped[list[CodeFileHashSQL]]:
        """
        A list of hashes for this file
        """
        return relationship("CodeFileHashSQL", back_populates="code_file", lazy="joined")

    # def update(self, new: CodeFileSQL) -> None:
    #     """
    #     Update this code file with new information.
    #     """

    #     # basic attributes
    #     # filename is immutable
    #     # self.filename = new.filename
    #     self.upstream_url = new.upstream_url
    #     self.version = new.version
    #     self.requires_python = new.requires_python
    #     self.is_yanked = new.is_yanked
    #     self.yanked_reason = new.yanked_reason
    #     self.size = new.size
    #     self.upload_time = new.upload_time

    #     # hashes
    #     if self.hashes_dict != new.hashes_dict:
    #         # taking incoming hashes and add new ones
    #         for h in new.hashes:
    #             # if we don't have this hash, add it
    #             if h.kind not in self.hashes:
    #                 h.code_file = self

    #             # don't update existing hashes

    #     # metadata file
    #     if self.metadata_file:
    #         if new.metadata_file:
    #             self.metadata_file.update(new.metadata_file)
    #     else:
    #         self.metadata_file = new.metadata_file


class CodeFile(PackageFile):
    """
    Pydantic model for CodeFileSQL
    """

    requires_python: str | None
    is_yanked: bool
    yanked_reason: str | None
    size: int | None
    upload_time: datetime.datetime | None
    metadata_file: MetadataFile | None = Field(exclude=True, default=None)
    hashes: list[CodeFileHash] = Field(exclude=True)

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

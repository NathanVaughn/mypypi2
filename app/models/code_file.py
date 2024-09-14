from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from flask import url_for
from sqlalchemy import Boolean, DateTime, Integer, Text
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

    requires_python: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    """
    Python version requirements
    """
    is_yanked: Mapped[bool] = mapped_column(Boolean, default=False)
    yanked_reason: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    """
    Yanked string. We always show yanked files, but we keep the value here.
    """
    size: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    """
    File size in bytes
    """
    upload_time: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    """
    Upload time of the file
    """
    # setting lazy=joined here will ensure that the data for the
    # metadata file is always returned when this is queried
    # This is a huge performance boost when rendering templates
    # with lots of files. Without this, every single record
    # with a metadata file would result in a seperate query.
    metadata_file: Mapped[MetadataFile | None] = relationship("MetadataFile", back_populates="code_file", lazy="joined")

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

    @property
    def download_url(self) -> str:
        """
        Return the download URL for this file through our proxy.
        """
        return url_for(
            "file.file_route",
            repository_slug=self.package.repository.slug,
            package_name=self.package.name,
            filename=self.filename,
            version=self.version_text,
            _external=True,
        )

    @property
    def html_download_url(self) -> str:
        """
        Returns the download URL for use with the HTML API.
        """
        url = self.download_url
        if self.hash_value:
            url += f"#{self.hash_value}"
        return url

    def update(self, new: CodeFile) -> None:
        """
        Update this code file with new information.
        """

        # basic attributes
        # filename is immutable
        # self.filename = new.filename
        self.upstream_url = new.upstream_url
        self.version = new.version
        self.requires_python = new.requires_python
        self.is_yanked = new.is_yanked
        self.yanked_reason = new.yanked_reason
        self.size = new.size
        self.upload_time = new.upload_time

        # hashes
        if self.hashes_dict != new.hashes_dict:
            # taking incoming hashes and add new ones
            for h in new.hashes:
                # if we don't have this hash, add it
                if h.kind not in self.hashes:
                    h.code_file = self

                # don't update existing hashes

        # metadata file
        if self.metadata_file:
            if new.metadata_file:
                self.metadata_file.update(new.metadata_file)
        else:
            self.metadata_file = new.metadata_file

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship

from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.code_file_hash import CodeFileHash  # pragma: no cover
    from app.models.metadata_file import MetadataFile  # pragma: no cover


class CodeFile(PackageFile, table=True):
    """
    This model represents a code file associated with a package.
    This is what actually appears in the list of files for a package.
    """

    requires_python: str | None = Field(default=None)
    """
    Python version requirements
    """
    is_yanked: bool = Field(default=False)
    yanked_reason: str | None = Field(default=None)
    """
    Yanked string. We always show yanked files, but we keep the value here.
    """
    size: int | None = Field(default=None)
    """
    File size in bytes
    """
    upload_time: datetime.datetime | None = Field(default=None)
    """
    Upload time of the file
    """
    # setting lazy=joined here will ensure that the data for the
    # metadata file is always returned when this is queried
    # This is a huge performance boost when rendering templates
    # with lots of files. Without this, every single record
    # with a metadata file would result in a seperate query.
    metadata_file: MetadataFile | None = Relationship(
        back_populates="code_file", sa_relationship_kwargs={"lazy": "joined"})

    hashes: Mapped[list["CodeFileHash"]] = Relationship(
        back_populates="code_file", sa_relationship_kwargs={"lazy": "joined"})

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

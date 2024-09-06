from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship

from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.code_file import CodeFile  # pragma: no cover
    from app.models.metadata_file_hash import MetadataFileHash  # pragma: no cover


class MetadataFile(PackageFile, table=True):
    """
    This model represents a metdata file for a code file associated with a package.
    These do not appear explicitly in the list of files for a package, but
    are the same as a code file with the extension of `.metadata`.
    """

    code_file_id: str = Field(foreign_key="code_file.id")
    code_file: "CodeFile" = Relationship(
        back_populates="metadata_file",  sa_relationship_kwargs={"lazy": "joined"})

    hashes: Mapped[list["MetadataFileHash"]] = Relationship(
        back_populates="metadata_file", sa_relationship_kwargs={"lazy": "joined"})

    def update(self, new: MetadataFile) -> None:
        """
        Update this metadata file with new information.
        """

        # basic attributes
        # filename is immutable
        # self.filename = new.filename
        self.upstream_url = new.upstream_url
        self.version = new.version

        # hashes
        if self.hashes_dict != new.hashes_dict:
            # taking incoming hashes and add new ones
            for h in new.hashes:
                # if we don't have this hash, add it
                if h.kind not in self.hashes:
                    h.metadata_file = self

                # don't update existing hashes

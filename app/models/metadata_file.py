from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.code_file import CodeFile  # pragma: no cover
    from app.models.metadata_file_hash import MetadataFileHash  # pragma: no cover


class MetadataFile(PackageFile):
    """
    This model represents a metdata file for a code file associated with a package.
    These do not appear explicitly in the list of files for a package, but
    are the same as a code file with the extension of `.metadata`.
    """

    __tablename__ = "metadata_file"

    code_file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("code_file.id"))
    code_file: Mapped[CodeFile] = relationship("CodeFile", back_populates="metadata_file", lazy="joined")

    @declared_attr
    def hashes(cls) -> Mapped[list[MetadataFileHash]]:
        """
        A list of hashes for this file
        """
        return relationship("MetadataFileHash", back_populates="metadata_file", lazy="joined")

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

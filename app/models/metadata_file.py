from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

import app.data.sql.main2
from app.models.code_file import CodeFile
from app.models.metadata_file_hash import MetadataFileHash
from app.models.package_file import PackageFile, PackageFileSQL

if TYPE_CHECKING:
    from app.models.code_file import (
        CodeFileSQL,  # pragma: no cover
    )
    from app.models.metadata_file_hash import MetadataFileHashSQL  # pragma: no cover


class MetadataFileSQL(PackageFileSQL):
    """
    This model represents a metdata file for a code file associated with a package.
    These do not appear explicitly in the list of files for a package, but
    are the same as a code file with the extension of `.metadata`.
    """

    __tablename__ = "metadata_file"

    code_file_id: Mapped[int] = mapped_column(ForeignKey("code_file.id"))
    code_file: Mapped[CodeFileSQL] = relationship(
        "CodeFileSQL", back_populates="metadata_file", lazy="joined")

    @declared_attr
    def hashes(cls) -> Mapped[list[MetadataFileHashSQL]]:
        """
        A list of hashes for this file
        """
        return relationship("MetadataFileHashSQL", back_populates="metadata_file", lazy="joined")

    # def update(self, new: MetadataFileSQL) -> None:
    #     """
    #     Update this metadata file with new information.
    #     """

    #     # basic attributes
    #     # filename is immutable
    #     # self.filename = new.filename
    #     self.upstream_url = new.upstream_url
    #     self.version = new.version

    #     # hashes
    #     if self.hashes_dict != new.hashes_dict:
    #         # taking incoming hashes and add new ones
    #         for h in new.hashes:
    #             # if we don't have this hash, add it
    #             if h.kind not in self.hashes:
    #                 h.metadata_file = self

    #             # don't update existing hashes


class MetadataFile(PackageFile):
    """
    Pydantic model for MetadataFileSQL
    """

    # code_file: "CodeFile" = Field(exclude=True)  # forward reference
    code_file_id: int | None = None  # comes from SQL model

    hashes: list[MetadataFileHash] = Field(exclude=True)

    @property
    def code_file(self) -> CodeFile:
        """
        Parent code file
        """
        assert self.code_file_id is not None
        return app.data.sql.main2.get_by_id(CodeFileSQL, self.code_file_id)

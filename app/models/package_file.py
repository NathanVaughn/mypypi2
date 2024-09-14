from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.package import Package  # pragma: no cover
    from app.models.package_file_hash import PackageFileHash  # pragma: no cover


class PackageFile(Base):
    """
    This model represents a file associated with a package.
    This is a base model meant to inherited.
    """

    __abstract__ = True
    __table_args__ = (UniqueConstraint("filename", "package_id"),)

    @declared_attr
    def package_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(ForeignKey("package.id"))

    @declared_attr
    def package(cls) -> Mapped[Package]:
        """
        The parent package
        """
        return relationship("Package", lazy="joined")

    filename: Mapped[str] = mapped_column(Text)
    """
    Package filename. Guaranteed to be unique for a repository.
    """
    upstream_url: Mapped[str] = mapped_column(Text)
    """
    Upstream URL where we can download this package
    """
    version: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    """
    For some files, record the version
    """
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    """
    Have we already downloaded this package?
    """

    @declared_attr
    def hashes(cls) -> Mapped[list[PackageFileHash]]:
        """
        This needs to be overridden in the subclasses.
        This is kept here for type checking only.
        """
        return relationship("PackageFileHash", lazy="joined")  # pragma: no cover

    # utility properties

    @property
    def version_text(self) -> str:
        """
        Returns the version text for this file.
        """
        return self.version or "UNKNOWN"

    @property
    def hashes_dict(self) -> dict[str, str]:
        """
        Returns a dictionary of all hashes for this file.
        Used in the JSON API.
        """
        return {hash.kind: hash.value for hash in self.hashes}

    @property
    def hash_value(self) -> str | None:
        """
        Returns the first hash value for this file.
        Use for the HTML API since files can have more than one hash,
        while the HTML API only supports one.

        Returns None if no hashes are available.
        """
        if not self.hashes:
            return None
        return f"{self.hashes[0].kind}={self.hashes[0].value}"

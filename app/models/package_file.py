from __future__ import annotations

from typing import TYPE_CHECKING

from flask import url_for
from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.package import Package
    from app.models.package_file_hash import PackageFileHash


class PackageFile(Base):
    __abstract__ = True
    __table_args__ = (
        UniqueConstraint("filename", "package_id",
                         name="_filename_package_id_uc"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """
    Unique identifier
    """

    @declared_attr
    def package_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("package.id"))

    @declared_attr
    def package(cls) -> Mapped[Package]:
        """
        The parent package
        """
        return relationship("Package", lazy="joined")

    filename: Mapped[str] = mapped_column(String)
    """
    Package filename. Guaranteed to be unique for a repository.
    """
    upstream_url: Mapped[str] = mapped_column(String)
    """
    Upstream URL where we can download this package
    """
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    """
    Have we already downloaded this package?
    """

    @declared_attr
    def hashes(cls) -> Mapped[list[PackageFileHash]]:
        """
        A list of hashes for this file
        """
        return relationship("PackageFileHash", back_populates="package_file")

    # utility properties

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

    @property
    def hashes_dict(self) -> dict[str, str]:
        """
        Returns a dictionary of all hashes for this file.
        Used in the JSON API.
        """
        return {hash.kind: hash.value for hash in self.hashes}

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

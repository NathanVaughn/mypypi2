from __future__ import annotations

from typing import TYPE_CHECKING

from flask import url_for
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.repository import Repository


class PackageVersionFilename(Base):
    __tablename__ = "package_version_filename"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """
    Unique identifier
    """
    repository_id: Mapped[int] = mapped_column(ForeignKey("repository.id"))
    repository: Mapped[Repository] = relationship("Repository")
    """
    The parent repository
    """
    package: Mapped[str] = mapped_column(String)
    """
    Package name
    """
    version: Mapped[str] = mapped_column(String)
    """
    Package version
    """
    filename: Mapped[str] = mapped_column(String, unique=True, index=True)
    """
    Package filename. Guaranteed to be unique.
    """
    python_requires: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    """
    Python version requirements
    """
    blake2b_256_hash: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    """
    BLAKE2b-256 hash of the file
    """
    md5_hash: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    """
    MD5 hash of the file
    """
    sha256_hash: Mapped[str] = mapped_column(String)
    """
    SHA256 hash of the file
    """
    upstream_url: Mapped[str] = mapped_column(String)
    """
    Upstream URL where we can download this package
    """
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    """
    Have we already downloaded this package?
    """
    dist_info_metadata_sha256_hash: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    """
    SHA256 hash of the metadata file, if available
    """
    core_metadata_sha256_hash: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    """
    SHA256 hash of the metadata file, if available
    """

    @property
    def download_url(self) -> str:
        return url_for(
            "file.file_route",
            package=self.package,
            version=self.version,
            filename=self.filename,
            _external=True,
        )

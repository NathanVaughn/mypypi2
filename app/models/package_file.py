from __future__ import annotations

from typing import TYPE_CHECKING

from flask import url_for
from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.repository import Repository


class PackageFile(Base):
    __abstract__ = True
    __table_args__ = (
        UniqueConstraint(
            "filename", "repository_id", name="_filename_repository_id_uc"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """
    Unique identifier
    """

    @declared_attr
    def repository_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("repository.id"))

    @declared_attr
    def repository(cls) -> Mapped[Repository]:
        return relationship("Repository")

    """
    The parent repository
    """
    package_name: Mapped[str] = mapped_column(String)
    """
    Package name
    """
    version: Mapped[str] = mapped_column(String)
    """
    Package version
    """
    filename: Mapped[str] = mapped_column(String)
    """
    Package filename. Guaranteed to be unique for a repository.
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

    @property
    def download_url(self) -> str:
        return url_for(
            "file.file_route",
            repository_slug=self.repository.slug,
            package_name=self.package_name,
            version=self.version,
            filename=self.filename,
            _external=True,
        )

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from pydantic import Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.code_file import CodeFile
from app.models.database import Base, BaseSQL
from app.models.repository import Repository

if TYPE_CHECKING:
    from app.models.code_file import CodeFileSQL  # pragma: no cover
    from app.models.repository import (
        Repository,  # pragma: no cover
        RepositorySQL,  # pragma: no cover
    )


class PackageSQL(BaseSQL):
    """
    This model represents a package in a repository.
    This records the name of the package, the last time the package data was updated,
    and is tied to a list of child files.
    """

    __tablename__ = "package"
    __table_args__ = (UniqueConstraint("name", "repository_id", name="_name_repository_id_uc"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """
    Unique identifier
    """
    repository_id: Mapped[int] = mapped_column(ForeignKey("repository.id"))
    repository: Mapped[RepositorySQL] = relationship("RepositorySQL")
    """
    The parent repository
    """
    name: Mapped[str] = mapped_column(String)
    """
    Package name
    """
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime)
    """
    Last time this package's data was updated
    """

    code_files: Mapped[list[CodeFileSQL]] = relationship("CodeFileSQL", back_populates="package")


class Package(Base):
    """
    Pydantic model for PackageSQL
    """

    id: int | None = None  # comes from SQL model
    repository: "Repository" = Field(exclude=True)  # forward reference
    repository_id: int | None = None  # comes from SQL model

    name: str
    last_updated: datetime.datetime = Field(default_factory=datetime.datetime.now)

    code_files: list[CodeFile] = Field(exclude=True)

    @property
    def is_current(self) -> bool:
        """
        Is the package data up-to-date?
        """
        return self.last_updated > datetime.datetime.now() - datetime.timedelta(minutes=self.repository.cache_minutes)

    @property
    def repository_url(self) -> str:
        """
        URL for this package in the repository
        """
        return f"{self.repository.simple_url}/{self.name}/"

    @property
    def log_name(self) -> str:
        """
        Package name for logging
        """
        return f"{self.repository.slug}:{self.name}"

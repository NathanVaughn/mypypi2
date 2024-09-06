from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.code_file import CodeFile  # pragma: no cover
    from app.models.repository import Repository  # pragma: no cover


class Package(Base, table=True):
    """
    This model represents a package in a repository.
    This records the name of the package, the last time the package data was updated,
    and is tied to a list of child files.
    """

    repository_id: str = Field(foreign_key="repository.id")
    repository: "Repository" = Relationship(back_populates="packages")
    """
    The parent repository
    """
    name: str
    """
    Package name
    """
    last_updated: datetime.datetime = Field(default=datetime.datetime.now)
    """
    Last time this package's data was updated
    """

    code_files: list["CodeFile"] = Relationship(back_populates="package")

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

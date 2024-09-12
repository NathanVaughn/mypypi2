from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.code_file import CodeFile  # pragma: no cover
    from app.models.repository import Repository  # pragma: no cover


class Package(Base):
    """
    This model represents a package in a repository.
    This records the name of the package, the last time the package data was updated,
    and is tied to a list of child files.
    """

    __tablename__ = "package"
    __table_args__ = (UniqueConstraint("name", "repository_id"),)

    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repository.id"))
    repository: Mapped[Repository] = relationship("Repository", lazy="joined", back_populates="packages")
    """
    The parent repository
    """
    name: Mapped[str] = mapped_column(String)
    """
    Package name
    """
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    """
    Last time this package's data was updated
    """

    code_files: Mapped[list[CodeFile]] = relationship("CodeFile", back_populates="package")

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

    @property
    def child_count(self) -> int:
        """
        Total number of objects
        """
        count = 0
        for code_file in self.code_files:
            count += 1
            count += len(code_file.hashes)
            if code_file.metadata_file:
                count += 1
                count += len(code_file.metadata_file.hashes)
        return count

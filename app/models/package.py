from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.code_file import CodeFile  # pragma: no cover
    from app.models.repository import Repository  # pragma: no cover


class Package(Base):
    __tablename__ = "package"
    __table_args__ = (
        UniqueConstraint("name", "repository_id", name="_name_repository_id_uc"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """
    Unique identifier
    """
    repository_id: Mapped[int] = mapped_column(ForeignKey("repository.id"))
    repository: Mapped[Repository] = relationship(
        "Repository", lazy="joined", back_populates="packages"
    )
    """
    The parent repository
    """
    name: Mapped[str] = mapped_column(String)
    """
    Package name
    """
    last_updated: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now
    )
    """
    Last time this package's data was updated
    """

    code_files: Mapped[list[CodeFile]] = relationship(
        "CodeFile", back_populates="package"
    )

    @property
    def is_current(self) -> bool:
        """
        Is the package data up-to-date?
        """
        return self.last_updated > datetime.datetime.now() - datetime.timedelta(
            minutes=self.repository.cache_minutes
        )

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BLOB, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.repository import Repository


class URLCache(Base):
    __tablename__ = "url_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String)
    """
    URL that was cached
    """
    repository_id: Mapped[int] = mapped_column(ForeignKey("repository.id"))
    repository: Mapped[Repository] = relationship("Repository")
    """
    The parent repository
    """
    http_response_code: Mapped[int] = mapped_column(Integer)
    """
    The HTTP response code receieved
    """
    contents: Mapped[bytes] = mapped_column(BLOB)
    """
    The contents of the URL
    """
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime)
    """
    Last time this URL was uploaded
    """

    @property
    def is_current(self) -> bool:
        """
        Is the package data up-to-date?
        """
        return self.last_updated > datetime.datetime.now() - datetime.timedelta(
            minutes=self.repository.cache_minutes
        )

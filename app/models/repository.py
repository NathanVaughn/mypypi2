from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.package import Package  # pragma: no cover


class Repository(Base):
    """
    This model represents a repository (index) of packages.
    This records the URL of the repository, the cache time, and the timeout,
    and is tied to a list of child packages.
    """

    __tablename__ = "repository"

    slug: Mapped[str] = mapped_column(Text, unique=True)
    """
    The repository slug
    """
    simple_url: Mapped[str] = mapped_column(Text)
    """
    The repository simple URL. Will have no trailing slash.
    Any value with a trailing slash provided will have it removed.
    """
    cache_minutes: Mapped[int] = mapped_column(Integer)
    """
    Number of minutes to cache package data for
    """
    timeout_seconds: Mapped[int] = mapped_column(Integer)
    """
    Number of seconds to wait for a response from the upstream server
    """

    packages: Mapped[list[Package]] = relationship("Package", back_populates="repository")

    @validates("simple_url")
    def validate_simple_url(self, key: str, simple_url: str) -> str:
        """
        Remove any trailing slashes from the simple URL and strip precedding/trailing whitespace
        """
        return simple_url.rstrip("/").strip()

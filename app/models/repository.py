from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.package import Package  # pragma: no cover


class Repository(Base):
    __tablename__ = "repository"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    """
    The repository slug
    """
    simple_url: Mapped[str] = mapped_column(String)
    """
    The repository simple URL. Will have no trailing slash.
    """
    cache_minutes: Mapped[int] = mapped_column(Integer)
    """
    Number of minutes to cache package data for
    """
    timeout_seconds: Mapped[int] = mapped_column(Integer)
    """
    Number of seconds to wait for a response from the upstream server
    """

    packages: Mapped[list[Package]] = relationship(
        "Package", back_populates="repository"
    )

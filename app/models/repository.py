from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import field_validator
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base, BaseSQL

if TYPE_CHECKING:
    from app.models.package import PackageSQL  # pragma: no cover


class RepositorySQL(BaseSQL):
    """
    This model represents a repository (index) of packages.
    This records the URL of the repository, the cache time, and the timeout,
    and is tied to a list of child packages.
    """

    __tablename__ = "repository"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    """
    The repository slug
    """
    simple_url: Mapped[str] = mapped_column(String)
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

    packages: Mapped[list[PackageSQL]] = relationship("PackageSQL", back_populates="repository")


class Repository(Base):
    """
    Pydantic model for RepositorySQL
    """

    id: int | None = None  # comes from SQL model
    slug: str
    simple_url: str
    cache_minutes: int
    timeout_seconds: int

    # this is a liability
    # packages: list[Package] = Field(exclude=True)

    @field_validator("simple_url")
    @classmethod
    def validate_simple_url(cls, simple_url: str) -> str:
        """
        Remove any trailing slashes from the simple URL and strip precedding/trailing whitespace
        """
        return simple_url.rstrip("/").strip()

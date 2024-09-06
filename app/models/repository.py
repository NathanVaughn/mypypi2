from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import field_validator
from sqlmodel import Field, Relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.package import Package  # pragma: no cover


class Repository(Base, table=True):
    """
    This model represents a repository (index) of packages.
    This records the URL of the repository, the cache time, and the timeout,
    and is tied to a list of child packages.
    """

    slug: str = Field(unique=True)
    """
    The repository slug
    """
    simple_url: str
    """
    The repository simple URL. Will have no trailing slash.
    Any value with a trailing slash provided will have it removed.
    """
    cache_minutes: int
    """
    Number of minutes to cache package data for
    """
    timeout_seconds: int
    """
    Number of seconds to wait for a response from the upstream server
    """

    packages: list["Package"] = Relationship(back_populates="repository")

    @field_validator("simple_url")
    @classmethod
    def validate_simple_url(cls, v: str) -> str:
        """
        Remove any trailing slashes from the simple URL and strip precedding/trailing whitespace
        """
        return v.rstrip("/").strip()

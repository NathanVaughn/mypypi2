from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class PackageFileHash(Base):
    """
    This model represents a content hash for a file associated with a package.
    Since the JSON API allows for files to have multiple hashes, we need a seperate
    table. This is a base model meant to inherited.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """
    Unique identifier
    """
    kind: Mapped[str] = mapped_column(String)
    """
    Type of hash of the file
    """
    value: Mapped[str] = mapped_column(String)
    """
    Hash of the file
    """

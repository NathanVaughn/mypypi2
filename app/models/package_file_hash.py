from __future__ import annotations

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class PackageFileHash(Base):
    """
    This model represents a content hash for a file associated with a package.
    Since the JSON API allows for files to have multiple hashes, we need a seperate
    table. This is a base model meant to inherited.
    """

    __abstract__ = True

    kind: Mapped[str] = mapped_column(Text)
    """
    Type of hash of the file
    """
    value: Mapped[str] = mapped_column(Text)
    """
    Hash of the file
    """

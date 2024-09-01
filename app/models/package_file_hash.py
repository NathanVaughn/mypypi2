from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class PackageFileHash(Base):
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

from __future__ import annotations

import datetime

from sqlalchemy import DateTime, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Cache(Base):
    """
    This model stores cache values for the application.
    """

    __tablename__ = "cache"

    key: Mapped[str] = mapped_column(String, unique=True)
    """
    Cache key
    """
    value: Mapped[bytes] = mapped_column(LargeBinary)
    """
    Cache value
    """
    expiration: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    """
    When this cache value expires
    """

    @property
    def is_expired(self) -> bool:
        """
        Is the cache value still valid?
        """
        return self.expiration < datetime.datetime.now()

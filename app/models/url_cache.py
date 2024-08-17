import datetime

from flask import current_app
from sqlalchemy import BLOB, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class URLCache(Base):
    __tablename__ = "url_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String, unique=True)
    """
    URL
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
            minutes=current_app.config["PACKAGE_UPDATE_INTERVAL_MINUTES"]
        )

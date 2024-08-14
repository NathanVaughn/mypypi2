import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class PackageUpdate(Base):
    __tablename__ = "package_update"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    package: Mapped[str] = mapped_column(String, unique=True)
    """
    Package name
    """
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime)
    """
    Last time we checked the available versions and files for this package
    """

import datetime

from base import Base
from sqlalchemy.orm import Mapped, mapped_column


class PackageUpdate(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    package: Mapped[str] = mapped_column(unique=True)
    """
    Package name
    """
    last_updated: Mapped[datetime.datetime] = mapped_column()
    """
    Last time we checked the available versions and files for this package
    """


from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Repository(Base):
    __tablename__ = "repository"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    """
    The repository slug
    """
    simple_url: Mapped[str] = mapped_column(String)
    """
    The repository simple URL
    """

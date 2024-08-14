from base import Base
from sqlalchemy.orm import Mapped, mapped_column


class PackageVersionFilename(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    package: Mapped[str] = mapped_column()
    """
    Package name
    """
    version: Mapped[str] = mapped_column()
    """
    Package version
    """
    filename: Mapped[str] = mapped_column(unique=True)
    """
    Package filename. Guaranteed to be unique.
    """
    python_requires: Mapped[str] = mapped_column()
    """
    Python version requirements
    """
    blake2b_256_hash: Mapped[str] = mapped_column()
    """
    BLAKE2b-256 hash of the file
    """
    md5_hash: Mapped[str] = mapped_column()
    """
    MD5 hash of the file
    """
    sha256_hash: Mapped[str] = mapped_column()
    """
    SHA256 hash of the file
    """
    upstream_url: Mapped[str] = mapped_column()
    """
    Upstream URL where we can download this package
    """
    is_cached: Mapped[bool] = mapped_column()
    """
    Have we already downloaded this package?
    """

    @property
    def cached_url(self) -> str:
        cached_url_prefix = "https://files.nathanv.me/pypi"
        return f"{cached_url_prefix}/{self.package}/{self.version}/{self.filename}"

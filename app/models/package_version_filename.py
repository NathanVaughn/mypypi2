from flask import current_app, url_for
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class PackageVersionFilename(Base):
    __tablename__ = "package_version_filename"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    package: Mapped[str] = mapped_column(String)
    """
    Package name
    """
    version: Mapped[str] = mapped_column(String)
    """
    Package version
    """
    filename: Mapped[str] = mapped_column(String, unique=True)
    """
    Package filename. Guaranteed to be unique.
    """
    python_requires: Mapped[str] = mapped_column(String)
    """
    Python version requirements
    """
    blake2b_256_hash: Mapped[str] = mapped_column(String)
    """
    BLAKE2b-256 hash of the file
    """
    md5_hash: Mapped[str] = mapped_column(String)
    """
    MD5 hash of the file
    """
    sha256_hash: Mapped[str] = mapped_column(String)
    """
    SHA256 hash of the file
    """
    upstream_url: Mapped[str] = mapped_column(String)
    """
    Upstream URL where we can download this package
    """
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    """
    Have we already downloaded this package?
    """
    metadata_sha256_hash: Mapped[str] = mapped_column(String, default=None)
    """
    SHA256 hash of the metadata file, if available
    """

    @property
    def cached_url(self) -> str:
        cached_url_prefix = current_app.config["S3_PUBLIC_URL_PREFIX"].removesuffix("/")
        return f"{cached_url_prefix}/{self.package}/{self.version}/{self.filename}"

    @property
    def download_url(self) -> str:
        return url_for(
            "file.file_route",
            package=self.package,
            version=self.version,
            filename=self.filename,
            _external=True,
        )

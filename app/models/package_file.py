from __future__ import annotations

from typing import TYPE_CHECKING

from flask import url_for
from sqlmodel import Field, Relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.package import Package  # pragma: no cover
    from app.models.package_file_hash import PackageFileHash  # pragma: no cover


class PackageFile(Base):
    """
    This model represents a file associated with a package.
    This is a base model meant to inherited.
    """

    package_id: str = Field(foreign_key="package.id")
    package: "Package" = Relationship()

    filename: str
    """
    Package filename. Guaranteed to be unique for a repository.
    """
    upstream_url: str
    """
    Upstream URL where we can download this package
    """
    version: str | None = Field(default=None)
    """
    For some files, record the version
    """
    is_cached: bool = Field(default=False)
    """
    Have we already downloaded this package?
    """
    hashes: list["PackageFileHash"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"})
    """
    This needs to be overridden in the subclasses.
    This is kept here for type checking only.
    """

    # utility properties

    @property
    def version_text(self) -> str:
        """
        Returns the version text for this file.
        """
        return self.version or "UNKNOWN"

    @property
    def hash_value(self) -> str | None:
        """
        Returns the first hash value for this file.
        Use for the HTML API since files can have more than one hash,
        while the HTML API only supports one.

        Returns None if no hashes are available.
        """
        if not self.hashes:
            return None
        return f"{self.hashes[0].kind}={self.hashes[0].value}"

    @property
    def hash_kinds(self) -> list[str]:
        """
        Returns a list of all hash kinds for this file.
        """
        return [h.kind for h in self.hashes]

    @property
    def hashes_dict(self) -> dict[str, str]:
        """
        Returns a dictionary of all hashes for this file.
        Used in the JSON API.
        """
        return {hash.kind: hash.value for hash in self.hashes}

    @property
    def download_url(self) -> str:
        """
        Return the download URL for this file through our proxy.
        """
        return url_for(
            "file.file_route",
            repository_slug=self.package.repository.slug,
            package_name=self.package.name,
            filename=self.filename,
            version=self.version_text,
            _external=True,
        )

    @property
    def html_download_url(self) -> str:
        """
        Returns the download URL for use with the HTML API.
        """
        url = self.download_url
        if self.hash_value:
            url += f"#{self.hash_value}"
        return url

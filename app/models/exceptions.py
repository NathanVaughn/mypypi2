from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from werkzeug.exceptions import HTTPException

from app.utils import log_package_name

if TYPE_CHECKING:
    from app.models.repository import Repository  # pragma: no cover


class UnknownFileFormat(Exception):
    """
    Exception raised when an unknown file format is encountered
    and the version cannot be parsed
    """


class UnknownStorageDriver(Exception):
    """
    Exception raised when an unknown storage driver is configured
    """


class InvalidQualityValue(Exception):
    """
    Exception raised when a quality value is invalid
    """


class RepositoryNotFound(HTTPException):
    """
    Exception raised when a repository is not found
    """

    code = HTTPStatus.NOT_FOUND

    def __init__(self, repository_slug: str):
        super().__init__(description=f"Repository {repository_slug} not found")


class PackageFileNotFound(HTTPException):
    """
    Exception raised when a repository is not found
    """

    code = HTTPStatus.NOT_FOUND

    def __init__(self, repository: Repository, package_name: str, filename: str):
        super().__init__(
            description=f"Package file {filename} not found in {
                log_package_name(repository, package_name)}"
        )

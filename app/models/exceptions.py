from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from werkzeug.exceptions import HTTPException

if TYPE_CHECKING:
    from app.models.package import Package  # pragma: no cover


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


class IndexTimeoutError(Exception):
    """
    Exception raised when a timeout occurs while fetching an index
    """


class PackageNotFound(HTTPException):
    """
    Exception raised when a repository is not found
    """

    code = HTTPStatus.NOT_FOUND

    def __init__(
        self,
        repository_slug: str,
        package_name: str,
    ):
        super().__init__(
            description=f"Package {
                package_name} not found in repository {repository_slug}"
        )


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

    def __init__(self, package: Package, filename: str):
        super().__init__(
            description=f"Package file {
                filename} not found in {package.log_name}"
        )


class IndexParsingError(HTTPException):
    """
    Exception raised when upstream index data cannot be parsed
    """

    code = HTTPStatus.SERVICE_UNAVAILABLE

    def __init__(self, url: str):
        super().__init__(description=f"Unable to parse {url}")

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

import flask

if TYPE_CHECKING:
    from app.models.package_version_filename import PackageVersionFilename


class BaseStorage(abc.ABC):
    def _get_path(self, package_version_filename: PackageVersionFilename) -> str:
        """
        Build the path to the file in storage
        """
        return f"{package_version_filename.package}/{package_version_filename.version}/{package_version_filename}"

    @abc.abstractmethod
    def cache_file(self, package_version_filename: PackageVersionFilename) -> None:
        """
        Upload a file
        """
        ...

    @abc.abstractmethod
    def download_file(self, package_version_filename: PackageVersionFilename) -> flask.Response:
        """
        Download a file
        """
        ...

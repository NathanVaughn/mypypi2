from __future__ import annotations

import abc
from typing import TYPE_CHECKING

import flask
from loguru import logger

if TYPE_CHECKING:
    from app.models.package_file import PackageFile


class BaseStorage(abc.ABC):
    def _get_path(self, package_file: PackageFile) -> str:
        """
        Build the path to the file in storage
        """
        return f"{package_file.repository.slug}/{package_file.package_name}/{package_file.filename}"

    @abc.abstractmethod
    def upload_file(self, package_file: PackageFile) -> None:
        """
        Upload a file
        """
        ...

    @abc.abstractmethod
    def check_file(self, package_file: PackageFile) -> bool:
        """
        Check if a file already exists
        """
        ...

    def cache_file(self, package_file: PackageFile) -> None:
        """
        Cache a file
        """
        if not self.check_file(package_file):
            self.upload_file(package_file)
        else:
            logger.info(f"File {package_file.filename} already exists")

    @abc.abstractmethod
    def download_file(self, package_file: PackageFile) -> flask.Response:
        """
        Download a file
        """
        ...

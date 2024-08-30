from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

import flask
import requests
from loguru import logger

from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.package_file import PackageFile


from app.data.storage.base import BaseStorage


class LocalStorage(BaseStorage):
    def __init__(self, directory: str) -> None:
        self._local_dir = pathlib.Path(directory)
        self._local_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, package_file: PackageFile) -> pathlib.Path:
        """
        Build the path to the file in local storage
        """
        return self._local_dir.joinpath(self._get_path(package_file))

    def upload_file(self, package_file: PackageFile) -> None:
        """
        Take a file from an upstream URL and save it
        """
        local_path = self._path(package_file)
        upstream_url = package_file.upstream_url

        logger.info(f"Downloading {upstream_url} to {local_path.absolute()}")
        with open(local_path, "wb") as fp:
            with requests.get(upstream_url, stream=True) as response:
                for chunk in response.iter_content(chunk_size=8192):
                    fp.write(chunk)

    def check_file(self, package_file: PackageFile) -> bool:
        """
        Check if a file already exists
        """
        return self._path(package_file).exists()

    def download_file(self, package_file: PackageFile) -> flask.BaseResponse:
        """
        Download a file
        """
        path = self._path(package_file)
        logger.debug(f"Sending {path}")
        return flask.send_file(path, as_attachment=True)

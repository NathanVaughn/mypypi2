from __future__ import annotations

from typing import TYPE_CHECKING

import flask
import s3fs
import werkzeug.wrappers.response
from loguru import logger

import app.http
from app.constants import DOWNLOAD_CHUNK_SIZE
from app.data.storage.base import BaseStorage
from app.models.package_file import PackageFile

if TYPE_CHECKING:
    from app.models.package_file import PackageFile


class S3Storage(BaseStorage):
    def __init__(
        self,
        endpoint_url: str,
        bucket_name: str,
        access_key_id: str,
        secret_access_key: str,
        public_url_prefix: str,
        region_name: str | None,
        bucket_prefix: str,
        redirect_code: int,
    ) -> None:
        self._bucket_name = bucket_name
        self._bucket_prefix = bucket_prefix.removesuffix("/")
        self._public_url_prefix = public_url_prefix.removesuffix("/")
        self._redirect_code = redirect_code

        self._interface = s3fs.S3FileSystem(
            endpoint_url=endpoint_url,
            key=access_key_id,
            secret=secret_access_key,
            client_kwargs={"region_name": region_name},
        )

    def _cache_path(self, package_file: PackageFile) -> str:
        """
        Build the path to the file in S3 for upload
        """
        return f"{self._bucket_name}/{self._bucket_prefix}/{self._get_path(package_file)}"

    def _download_path(self, package_file: PackageFile) -> str:
        """
        Build the path to the file in S3
        """
        return f"{self._public_url_prefix}/{self._get_path(package_file)}"

    def check_file(self, package_file: PackageFile) -> bool:
        """
        Check if the file already exists in S3
        """
        s3_url = self._cache_path(package_file)
        return self._interface.exists(s3_url)

    def upload_file(self, package_file: PackageFile) -> None:
        """
        Take a file from an upstream URL and save it
        """
        s3_url = self._cache_path(package_file)
        upstream_url = package_file.upstream_url

        logger.debug(f"Uploading {upstream_url} to {s3_url}")
        with self._interface.open(s3_url, "wb") as fp:
            with app.http.stream(upstream_url) as response:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    fp.write(chunk)

    def download_file(self, package_file: PackageFile) -> werkzeug.wrappers.response.Response:
        """
        Download a file
        """
        path = self._download_path(package_file)
        logger.debug(f"Redirecting to {path}")
        return flask.redirect(
            self._download_path(package_file),
            code=self._redirect_code,
        )

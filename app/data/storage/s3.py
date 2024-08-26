from __future__ import annotations

import http
from typing import TYPE_CHECKING

import flask
import requests
import s3fs
from loguru import logger

if TYPE_CHECKING:
    from app.models.package_file import PackageFile


from app.data.storage.base import BaseStorage


class S3Storage(BaseStorage):
    def __init__(
        self,
        endpoint_url: str,
        bucket_name: str,
        access_key_id: str,
        secret_access_key: str,
        public_url_prefix: str,
        region_name: str | None = None,
        bucket_prefix: str = "",
    ) -> None:
        self._bucket_name = bucket_name
        self._bucket_prefix = bucket_prefix.removesuffix("/")
        self._public_url_prefix = public_url_prefix.removesuffix("/")

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
        return (
            f"{self._bucket_name}/{self._bucket_prefix}/{self._get_path(package_file)}"
        )

    def _download_path(self, package_file: PackageFile) -> str:
        """
        Build the path to the file in S3
        """
        return f"{self._public_url_prefix}/{self._get_path(package_file)}"

    def cache_file(self, package_file: PackageFile) -> None:
        """
        Take a file from an upstream URL and save it
        """
        s3_url = self._cache_path(package_file)
        upstream_url = package_file.upstream_url

        logger.info(f"Uploading {upstream_url} to {s3_url}")
        with self._interface.open(s3_url, "wb") as fp:
            with requests.get(upstream_url, stream=True) as response:
                for chunk in response.iter_content(chunk_size=8192):
                    fp.write(chunk)

    def download_file(self, package_file: PackageFile) -> flask.BaseResponse:
        """
        Download a file
        """
        return flask.redirect(
            self._download_path(package_file),
            code=http.HTTPStatus.PERMANENT_REDIRECT,
        )
from __future__ import annotations

from typing import TYPE_CHECKING

from flask import current_app

if TYPE_CHECKING:
    from app.models.package_version_filename import PackageVersionFilename


def _build_s3_path(package_version_filename: PackageVersionFilename) -> str:
    """
    Build the path to the file in S3
    """
    return f"{package_version_filename.package}/{package_version_filename.version}/{package_version_filename.filename}"


def upload_path(package_version_filename: PackageVersionFilename) -> str:
    """
    Build the path to the file in S3
    """
    bucket_prefix = current_app.config["S3_BUCKET_PREFIX"].removesuffix("/")
    return f"{current_app.config['S3_BUCKET_NAME']}/{bucket_prefix}/{_build_s3_path(package_version_filename)}"


def download_path(package_version_filename: PackageVersionFilename) -> str:
    """
    Build the path to the file in S3
    """
    url_prefix = current_app.config["S3_PUBLIC_URL_PREFIX"].removesuffix("/")
    return f"{url_prefix}/{_build_s3_path(package_version_filename)}"

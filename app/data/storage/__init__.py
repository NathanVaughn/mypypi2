from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


class _ActiveStorage:
    def init_app(self, flask_app: Flask) -> None:
        with flask_app.app_context():
            if flask_app.config["storage"]["driver"] == "s3":
                import app.data.storage.s3

                s3_config: dict[str, str] = flask_app.config["storage"]["s3"]

                self.provider = app.data.storage.s3.S3Storage(
                    endpoint_url=s3_config["endpoint_url"],
                    bucket_name=s3_config["bucket_name"],
                    access_key_id=s3_config["access_key_id"],
                    secret_access_key=s3_config["secret_access_key"],
                    region_name=s3_config.get("region_name"),
                    public_url_prefix=s3_config["public_url_prefix"],
                    bucket_prefix=s3_config.get("bucket_prefix", ""),
                    redirect_code=int(
                        s3_config.get("redirect_code", HTTPStatus.PERMANENT_REDIRECT)
                    ),
                )
            elif flask_app.config["storage"]["driver"] == "local":
                import app.data.storage.local

                local_config = flask_app.config["storage"]["local"]

                self.provider = app.data.storage.local.LocalStorage(
                    directory=local_config["directory"],
                )
            else:
                raise ValueError("Unknown storage driver")


ActiveStorage = _ActiveStorage()

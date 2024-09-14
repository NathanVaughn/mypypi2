from __future__ import annotations

from app.config import Config, StorageDrivers

if Config.storage.driver == StorageDrivers.S3:
    import app.data.storage.s3

    assert Config.storage.s3 is not None

    StorageDriver = app.data.storage.s3.S3Storage(
        endpoint_url=str(Config.storage.s3.endpoint_url),
        bucket_name=Config.storage.s3.bucket_name,
        access_key_id=Config.storage.s3.access_key_id,
        secret_access_key=Config.storage.s3.secret_access_key,
        region_name=Config.storage.s3.region_name,
        public_url_prefix=Config.storage.s3.public_url_prefix,
        bucket_prefix=Config.storage.s3.bucket_prefix,
        redirect_code=Config.storage.s3.redirect_code,
    )

elif Config.storage.driver == StorageDrivers.LOCAL:
    import app.data.storage.local

    assert Config.storage.local is not None

    StorageDriver = app.data.storage.local.LocalStorage(
        directory=Config.storage.local.directory,
    )

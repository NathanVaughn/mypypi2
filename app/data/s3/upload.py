import requests
import s3fs
from loguru import logger


def upload_file(s3_options: dict, upstream_url: str, s3_url: str) -> None:
    """
    Cache a file
    """

    s3 = s3fs.S3FileSystem(
        endpoint_url=s3_options["endpoint_url"],
        key=s3_options["access_key_id"],
        secret=s3_options["secret_access_key"],
        client_kwargs={"region_name": s3_options["region_name"]},
    )

    logger.info(f"Uploading {upstream_url} to {s3_url}")
    with s3.open(s3_url, "wb") as fp:
        with requests.get(upstream_url, stream=True) as response:
            for chunk in response.iter_content(chunk_size=8192):
                fp.write(chunk)

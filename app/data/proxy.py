import datetime

import requests
from loguru import logger

from app.models.database import db
from app.models.url_cache import URLCache


def fetch_url(url: str) -> URLCache:
    """
    Fetch a URL and return the database object
    """
    # check last updated time
    url_cache: URLCache | None = db.session.execute(
        db.select(URLCache).filter_by(url=url)
    ).scalar_one_or_none()

    # check if url cache is current
    if url_cache is not None and url_cache.is_current:
        return url_cache

    # make the request
    logger.info(f"Fetching {url}")
    response = requests.get(url)

    # add it to the database
    if url_cache is None:
        url_cache = URLCache(
            url=url,
            http_response_code=response.status_code,
            contents=response.content,
            last_updated=datetime.datetime.now(),
        )
        db.session.add(url_cache)
    else:
        url_cache.http_response_code = response.status_code
        url_cache.contents = response.content
        url_cache.last_updated = datetime.datetime.now()

    # commit the transaction
    db.session.commit()

    return url_cache

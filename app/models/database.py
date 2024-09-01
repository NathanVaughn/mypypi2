from __future__ import annotations

from typing import TYPE_CHECKING

from flask_sqlalchemy import SQLAlchemy
from loguru import logger
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from flask import Flask


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def init_db(flask_app: Flask) -> None:
    # import models so sqlalchemy knows about them
    from app.models.code_file import CodeFile  # noqa
    from app.models.code_file_hash import CodeFileHash  # noqa
    from app.models.metadata_file import MetadataFile  # noqa
    from app.models.metadata_file_hash import MetadataFileHash  # noqa
    from app.models.package import Package  # noqa
    from app.models.repository import Repository  # noqa

    with flask_app.app_context():
        logger.debug("Initializing database")
        db.create_all()

        # load configured repositories
        import app.data.sql

        for repository in flask_app.config["repositories"]:
            slug = repository["slug"]
            simple_url = repository["simple_url"].removesuffix("/")
            cache_minutes = repository["cache_minutes"]
            timeout_seconds = repository["timeout_seconds"]

            repository = app.data.sql.get_repository(slug)

            if repository is None:
                # create new repository if it doesn't exist
                logger.debug(f"Adding repository {slug}")
                db.session.add(
                    Repository(
                        slug=slug,
                        simple_url=simple_url,
                        cache_minutes=cache_minutes,
                        timeout_seconds=timeout_seconds,
                    )
                )
            else:
                # update existing repository
                repository.simple_url = simple_url
                repository.cache_minutes = cache_minutes
                repository.timeout_seconds = timeout_seconds

        db.session.commit()

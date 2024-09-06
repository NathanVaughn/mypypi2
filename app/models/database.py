from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from flask_sqlalchemy import SQLAlchemy
from loguru import logger
from sqlmodel import Field, SQLModel

from app.config import Config

if TYPE_CHECKING:
    from flask import Flask


class Base(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    """
    Unique identifier
    Use a factory function so we can pre-generate these for speed
    """


db = SQLAlchemy(model_class=Base)


def init_db(flask_app: Flask) -> None:
    db.init_app(flask_app)

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

        for repository_config in Config.repositories:
            repository = app.data.sql.get_repository(repository_config.slug)

            if repository is None:
                # create new repository if it doesn't exist
                logger.debug(f"Adding repository {repository_config.slug}")
                db.session.add(
                    Repository(
                        slug=repository_config.slug,
                        simple_url=str(repository_config.simple_url),
                        cache_minutes=repository_config.cache_minutes,
                        timeout_seconds=repository_config.timeout_seconds,
                    )
                )
            else:
                # update existing repository
                repository.simple_url = str(repository_config.simple_url)
                repository.cache_minutes = repository_config.cache_minutes
                repository.timeout_seconds = repository_config.timeout_seconds

        db.session.commit()

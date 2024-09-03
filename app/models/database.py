from __future__ import annotations

from typing import TYPE_CHECKING

from flask_sqlalchemy import SQLAlchemy
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_mixins.serialize import SerializeMixin

from app.config import Config

if TYPE_CHECKING:
    from flask import Flask


class BaseSQL(DeclarativeBase, SerializeMixin):
    pass


class Base(BaseModel):
    class Config:
        from_attributes = True


db = SQLAlchemy(model_class=BaseSQL)


def init_db(flask_app: Flask) -> None:
    db.init_app(flask_app)

    # import models so sqlalchemy knows about them
    from app.models.code_file import CodeFileSQL  # noqa
    from app.models.code_file_hash import CodeFileHashSQL  # noqa
    from app.models.metadata_file import MetadataFileSQL  # noqa
    from app.models.metadata_file_hash import MetadataFileHashSQL  # noqa
    from app.models.package import PackageSQL  # noqa
    from app.models.repository import RepositorySQL, Repository  # noqa

    with flask_app.app_context():
        logger.debug("Initializing database")
        db.create_all()

        # load configured repositories
        import app.data.sql.main

        for repository_config in Config.repositories:
            repository = app.data.sql.main.get_repository(
                repository_config.slug)

            if repository is None:
                # create new repository if it doesn't exist
                logger.debug(f"Adding repository {repository_config.slug}")
                db.session.add(
                    RepositorySQL(
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

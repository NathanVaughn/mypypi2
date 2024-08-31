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
    from app.models.metadata_file import MetadataFile  # noqa
    from app.models.package import Package  # noqa
    from app.models.package_file_hash import PackageFileHash  # noqa
    from app.models.repository import Repository  # noqa

    with flask_app.app_context():
        logger.debug("Initializing database")
        db.create_all()

        # load configured repositories
        import app.data.sql

        for repository in flask_app.config["repositories"]:
            slug = repository["slug"]
            repository_obj = app.data.sql.lookup_repository(slug)

            if repository_obj is None:
                # create new repository if it doesn't exist
                logger.debug(f"Adding repository {slug}")
                db.session.add(
                    Repository(
                        slug=slug,
                        simple_url=repository["simple_url"].removesuffix("/"),
                        cache_minutes=repository["cache_minutes"],
                        timeout_seconds=repository["timeout_seconds"],
                    )
                )
            else:
                # update existing repository
                repository_obj.simple_url = repository["simple_url"].removesuffix(
                    "/")
                repository_obj.cache_minutes = repository["cache_minutes"]
                repository_obj.timeout_seconds = repository["timeout_seconds"]

        db.session.commit()

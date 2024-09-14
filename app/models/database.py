from __future__ import annotations

import os
import time
import uuid
from typing import TYPE_CHECKING

import psycogreen.eventlet
import sqlalchemy.exc
import ulid
from flask_sqlalchemy import SQLAlchemy
from loguru import logger
from sqlalchemy import Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import Config

if TYPE_CHECKING:
    from flask import Flask


class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=lambda: ulid.new().uuid, sort_order=-1)
    """
    Unique identifier. Uses a ULID to ensure no collisions.
    """
    # using a value that is not auto-incrementing is a huge performance gain.
    # Otherwise, the SQL database wants to insert one record at a time to be
    # able to generate the next ID. By generating the ID client-side,
    # we can use that ID pre-emptively in child foreign keys and not
    # have to wait for the parents to be inserted first.


db = SQLAlchemy(model_class=Base)


def init_db(flask_app: Flask) -> None:
    psycogreen.eventlet.patch_psycopg()

    # with multiple workers, make sure 10 aren't trying to
    # create tables all at the same time
    # easiest fix is to sleep based on their ID, so they are hopefully sequential
    # Docker always seems to start at PID 8
    worker_id = int(os.getenv("GUNICORN_WORKER_ID", 8)) - 7
    # make sure there are no negative values
    time.sleep(max(0, worker_id))

    db.init_app(flask_app)

    # import models so sqlalchemy knows about them
    from app.models.code_file import CodeFile  # noqa
    from app.models.code_file_hash import CodeFileHash  # noqa
    from app.models.metadata_file import MetadataFile  # noqa
    from app.models.metadata_file_hash import MetadataFileHash  # noqa
    from app.models.package import Package  # noqa
    from app.models.repository import Repository  # noqa
    from app.models.cache import Cache  # noqa

    with flask_app.app_context():
        ready = False
        while not ready:
            try:
                db.session.execute(text("SELECT 1"))
                ready = True
            except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.ProgrammingError):
                logger.info("Waiting for database to be ready")
                time.sleep(1)

        logger.debug("Initializing database")
        # this will not create tables if they already exist
        db.create_all()

        import app.data.sql

        # load configured repositories
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
        logger.success("Database ready")

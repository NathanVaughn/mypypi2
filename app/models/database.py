from __future__ import annotations

from typing import TYPE_CHECKING

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from flask import Flask


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def init_db(flask_app: Flask) -> None:
    # import models so sqlalchemy knows about them
    from app.models.package_update import PackageUpdate  # noqa
    from app.models.package_code_file import PackageCodeFile  # noqa
    from app.models.package_metadata_file import PackageMetadataFile  # noqa
    from app.models.url_cache import URLCache  # noqa
    from app.models.repository import Repository  # noqa

    with flask_app.app_context():
        db.create_all()

        # load configured repositories
        import app.data.sql

        for repository in flask_app.config["repositories"]:
            repository_obj = app.data.sql.lookup_repository(repository["slug"])
            if repository_obj is None:
                # create new repository if it doesn't exist
                db.session.add(
                    Repository(
                        slug=repository["slug"],
                        simple_url=repository["simple_url"].removesuffix("/"),
                        cache_minutes=repository["cache_minutes"],
                    )
                )
            else:
                # update existing repository
                repository_obj.simple_url = repository["simple_url"].removesuffix("/")
                repository_obj.cache_minutes = repository["cache_minutes"]

        db.session.commit()

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
    from app.models.package_version_filename import PackageVersionFilename  # noqa

    with flask_app.app_context():
        db.create_all()

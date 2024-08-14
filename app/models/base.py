from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from app.app import flask_app


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(flask_app, model_class=Base)


def init_db() -> None:
    with flask_app.app_context():
        db.create_all()

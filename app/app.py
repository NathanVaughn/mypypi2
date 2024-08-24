import tomllib
from flask import Flask


def create_app():
    flask_app = Flask(__name__)
    with open("config.toml", "rb") as f:
        flask_app.config.update(tomllib.load(f))

    # setup database
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = flask_app.config["database"]["uri"]
    import app.models.database

    app.models.database.db.init_app(flask_app)
    app.models.database.init_db(flask_app)

    # setup storage
    import app.data.storage.active

    app.data.storage.active.ActiveStorage.init_app(flask_app)

    # setup routes
    from app.routes.file import file_bp
    from app.routes.simple import simple_bp

    flask_app.register_blueprint(simple_bp)
    flask_app.register_blueprint(file_bp)

    return flask_app

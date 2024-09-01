import tomllib
from flask import Flask


def create_app(is_testing: bool = False) -> Flask:
    flask_app = Flask(__name__)

    if is_testing:
        flask_app.config["TESTING"] = True
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        flask_app.config["storage"] = {"driver": "local", "local": {"directory": "tmp/storage"}}
        flask_app.config["repositories"] = []

    else:
        with open("config.toml", "rb") as f:
            flask_app.config.update(tomllib.load(f))

        flask_app.config["SQLALCHEMY_DATABASE_URI"] = flask_app.config["database"]["uri"]

    # setup database
    # flask_app.config["SQLALCHEMY_ECHO"] = True
    import app.models.database

    app.models.database.db.init_app(flask_app)
    app.models.database.init_db(flask_app)

    # setup storage
    import app.data.storage

    app.data.storage.ActiveStorage.init_app(flask_app)

    # setup routes
    from app.routes.file import file_bp
    from app.routes.simple import simple_bp

    flask_app.register_blueprint(simple_bp)
    flask_app.register_blueprint(file_bp)

    return flask_app

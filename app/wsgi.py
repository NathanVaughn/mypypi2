import os

from flask import Flask

from app.config import Config, StorageDrivers, StorageFilesystemConfig


def create_app(is_testing: bool = False) -> Flask:
    flask_app = Flask(__name__)

    # load configuration
    if is_testing:
        flask_app.config["TESTING"] = True
        Config.database.url = "sqlite:///:memory:"
        Config.storage.driver = StorageDrivers.FILESYSTEM
        Config.storage.filesystem = StorageFilesystemConfig(directory=os.path.join("tmp", "storage"))
        Config.repositories = []

    # setup database
    # flask_app.config["SQLALCHEMY_ECHO"] = True
    import app.models.database

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = Config.database.url
    app.models.database.init_db(flask_app)

    # setup routes
    from app.routes.file import file_bp
    from app.routes.simple import simple_bp

    flask_app.register_blueprint(simple_bp)
    flask_app.register_blueprint(file_bp)

    return flask_app

import os

from flask import Flask, Response, request
from loguru import logger

from app.config import StorageDrivers, StorageFilesystemConfig, _Config

Config = _Config()  # type: ignore


def init_app() -> None:
    """
    This function should be called once before workers start to initialize the application
    and database.
    """
    flask_app = Flask(__name__)
    import app.models.database

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = Config.database.url
    app.models.database.init_db(flask_app, create=True)


def create_app(is_testing: bool = False) -> Flask:
    """
    This is the main WSGI entrypoint
    """
    flask_app = Flask(__name__)

    @flask_app.before_request
    def log_before_request() -> None:
        logger.info(f"{request.method} {request.full_path}")

    @flask_app.after_request
    def log_after_request(response: Response) -> Response:
        text = f"{response.status_code} {request.full_path}"
        if response.location:
            # show redirect
            text = f"{text} {response.location}"

        logger.info(text)
        return response

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
    from app.routes.favicon import favicon_bp
    from app.routes.file import file_bp
    from app.routes.healthcheck import healthcheck_bp
    from app.routes.simple import simple_bp

    flask_app.register_blueprint(favicon_bp)
    flask_app.register_blueprint(file_bp)
    flask_app.register_blueprint(healthcheck_bp)
    flask_app.register_blueprint(simple_bp)

    return flask_app

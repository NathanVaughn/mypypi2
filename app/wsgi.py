from flask import Flask, Response, request
from loguru import logger

from app.config import Config


def init_app() -> None:
    """
    This function should be called once before workers start to initialize the application
    and database.
    """
    flask_app = Flask(__name__)
    import app.models.database

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = Config.database.url
    app.models.database.init_db(flask_app, create=True)


def create_app() -> Flask:
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

    # set some variables for external urls
    # https://flask.palletsprojects.com/en/stable/config/#SERVER_NAME
    flask_app.config["SERVER_NAME"] = Config.base_url.host
    flask_app.config["PREFERRED_URL_SCHEME"] = Config.base_url.scheme
    flask_app.config["APPLICATION_ROOT"] = Config.base_url.path

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

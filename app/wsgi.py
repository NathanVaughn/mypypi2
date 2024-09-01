from flask import Flask

from app.config import Config, StorageLocalConfig


def create_app(is_testing: bool = False) -> Flask:
    flask_app = Flask(__name__)

    # load configuration
    if is_testing:
        flask_app.config["TESTING"] = True
        Config.database.uri = "sqlite:///:memory:"
        Config.storage.driver = "local"
        Config.storage.local = StorageLocalConfig(directory="tmp/storage")
        Config.repositories = []

    # setup database
    # flask_app.config["SQLALCHEMY_ECHO"] = True
    import app.models.database

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = Config.database.uri
    app.models.database.init_db(flask_app)

    # setup routes
    from app.routes.file import file_bp
    from app.routes.simple import simple_bp

    flask_app.register_blueprint(simple_bp)
    flask_app.register_blueprint(file_bp)

    return flask_app

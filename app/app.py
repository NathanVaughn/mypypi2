from flask import Flask


def create_app():
    flask_app = Flask(__name__)
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

    import app.models.database

    app.models.database.db.init_app(flask_app)
    app.models.database.init_db(flask_app)

    from app.routes.simple import simple_bp

    flask_app.register_blueprint(simple_bp)

    return flask_app

from flask import Flask

import app.models.base

flask_app = Flask(__name__)
flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

app.models.base.db.init_app(flask_app)
app.models.base.init_db()

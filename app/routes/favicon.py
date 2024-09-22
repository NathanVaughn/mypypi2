from flask import Blueprint, send_from_directory

from app.constants import ASSETS_DIRECTORY

favicon_bp = Blueprint("favicon", __name__)


@favicon_bp.route("/favicon.ico")
def favicon():
    return send_from_directory(ASSETS_DIRECTORY, "logo.ico")

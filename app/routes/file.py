from flask import Blueprint

import app.data.sql
import app.data.storage
import app.packages.data
from app.data.cache.decorator import repository_cache

file_bp = Blueprint("file", __name__)


@file_bp.route("/<string:repository_slug>/file/<string:version>/<string:package_name>/<string:filename>")
@repository_cache
def file_route(repository_slug: str, version: str, package_name: str, filename: str):
    """
    This route is used to download a specific file
    """
    package_file = app.packages.data.get_package_file(repository_slug, package_name, filename)

    return app.data.storage.ActiveStorage.provider.download_file(package_file)

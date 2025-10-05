from flask import Blueprint

import app.data.sql
import app.data.storage.active
import app.packages.data
from app.data.cache.wrappers import cache_repository_timeout_decorator

file_bp = Blueprint("file", __name__)


@file_bp.route("/<string:repository_slug>/file/<string:package_name>/<string:version>/<string:filename>")
@cache_repository_timeout_decorator
def file_route(repository_slug: str, package_name: str, version: str, filename: str):
    """
    This route is used to download a specific file
    """
    # this is not cached permamently because the file could potentially not exist
    # and then exist at a future time
    package_file = app.packages.data.get_package_file(repository_slug, package_name, filename)

    return app.data.storage.active.StorageDriver.send_file(package_file)

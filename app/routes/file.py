from flask import Blueprint

import app.data.packages
import app.data.sql
import app.data.storage.active

file_bp = Blueprint("file", __name__)


@file_bp.route(
    "/<string:repository_slug>/file/<string:package_name>/<string:version>/<string:filename>"
)
def file_route(repository_slug: str, package_name: str, version: str, filename: str):
    """
    This route is used to download a specific file
    """
    package_file = app.data.packages.get_package_file(
        repository_slug, package_name, filename
    )

    return app.data.storage.active.ActiveStorage.provider.download_file(package_file)

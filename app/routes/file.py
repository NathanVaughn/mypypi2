import http

from flask import Blueprint, abort, redirect

import app.data.packages
import app.data.sql

file_bp = Blueprint("file", __name__)


@file_bp.route("/<string:repository_slug>/file/<string:package>/<string:version>/<string:filename>")
def file_route(repository_slug: str, package: str, version: str, filename: str):
    """
    This route is used to download a specific file
    """
    # try to find the file in the database
    package_version_filename = app.data.sql.lookup_package_version_filename(
        repository_slug, filename)

    if not package_version_filename:
        # refresh the package data
        app.data.packages.update_package_data(package)

        # try again
        package_version_filename = app.data.sql.lookup_package_version_filename(
            repository_slug, filename)

        # now fail if still not found
        if not package_version_filename:
            return abort(http.HTTPStatus.NOT_FOUND)

    # if we haven't cached the file yet, do so now
    if not package_version_filename.is_cached:
        app.data.packages.cache_file(package_version_filename)

    # return a redirect to the cached file
    return redirect(
        package_version_filename.cached_url, http.HTTPStatus.PERMANENT_REDIRECT
    )

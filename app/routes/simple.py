from flask import Blueprint, render_template

import app.data.packages

simple_bp = Blueprint("simple", __name__)


@simple_bp.route("/<string:repository_slug>/simple/<string:package>/")
def simple_route(repository_slug: str, package: str):
    """
    This route is used to provide a simple index of a specific package
    """
    return render_template(
        "simple.html.j2",
        package=package,
        package_version_filenamess=app.data.packages.get_package_version_filenames(
            repository_slug,
            package,
        ),
    )

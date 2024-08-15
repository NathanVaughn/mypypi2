from flask import Blueprint, render_template

import app.data.packages

simple_bp = Blueprint("simple", __name__, url_prefix="/simple")


@simple_bp.route("/<string:package>/")
def simple_route(package: str):
    """
    This route is used to provide a simple index of a specific package
    """
    return render_template(
        "simple.html.j2",
        package=package,
        package_version_filenamess=app.data.packages.get_package_version_filenames(
            package
        ),
    )

from flask import Blueprint, render_template

import app.data.packages

simple_bp = Blueprint("simple", __name__)


@simple_bp.route("/<string:repository_slug>/simple/<string:package_name>/")
def simple_route(repository_slug: str, package_name: str):
    """
    This route is used to provide a simple index of a specific package
    """
    return render_template(
        "simple.html.j2",
        package_name=package_name,
        package_code_files=app.data.packages.get_package_code_files(
            repository_slug,
            package_name,
        ),
    )

from http import HTTPStatus

from flask import Blueprint, Response, redirect, render_template, request, url_for

import app.packages.lookup
import app.packages.simple
import app.templates.simple_json
from app.caching import repository_cache

simple_bp = Blueprint("simple", __name__)


@simple_bp.route("/")
@repository_cache
def simple_route_index():
    """
    Base index route, which we do not support.
    """
    return Response("Not Implemented", status=HTTPStatus.NOT_IMPLEMENTED)


@simple_bp.route("/<string:repository_slug>/simple/<string:package_name>")
@repository_cache
def simple_route_missing_trailing_slash(repository_slug: str, package_name: str):
    """
    Redirects to the same route with a trailing slash
    https://packaging.python.org/en/latest/specifications/simple-repository-api/#base-html-api
    > "All URLs which respond with an HTML5 page MUST end with a `/` and the repository
    > SHOULD redirect the URLs without a `/` to add a `/` to the end."
    """
    # two birds with one stone, normalize the name as well
    # redirect to the version with the trailing slash
    return redirect(
        code=HTTPStatus.MOVED_PERMANENTLY,
        location=url_for(
            "simple.simple_route",
            repository_slug=repository_slug,
            package_name=app.packages.simple.normalize_name(package_name),
        ),
    )


@simple_bp.route("/<string:repository_slug>/simple/<string:package_name>/")
@repository_cache
def simple_route(repository_slug: str, package_name: str):
    """
    This route is used to provide a simple index of a specific package
    """
    # per PEP 503, we can optionally redirect to the normalized name
    # https://peps.python.org/pep-0503/#normalized-names
    normalized_name = app.packages.simple.normalize_name(package_name)
    if normalized_name != package_name:
        return redirect(
            code=HTTPStatus.MOVED_PERMANENTLY,
            location=url_for(
                "simple.simple_route",
                repository_slug=repository_slug,
                package_name=normalized_name,
            ),
        )

    # handle incoming accept header and decide which version to return
    # https://peps.python.org/pep-0691/#version-format-selection
    accept_header = request.headers.get("Accept")
    format_query = request.args.get("format")
    index_format = app.packages.simple.determine_index_format(
        accept_header, format_query
    )

    # if we have no acceptable format, return a 406
    if index_format is None:
        return Response("Not Acceptable", status=HTTPStatus.NOT_ACCEPTABLE)

    # get the package information
    # this function will update the data if needed as well
    package = app.packages.lookup.get_package(
        repository_slug,
        package_name,
    )

    # if the package is not found, return a 404
    if package is None:
        return Response("Not Found", status=HTTPStatus.NOT_FOUND)

    # render the appropriate template
    if index_format == app.packages.simple.IndexFormat.json:
        response_content = app.templates.simple_json.render_template(package)
    elif index_format == app.packages.simple.IndexFormat.html:
        response_content = render_template(
            "simple.html.j2",
            package=package,
        )

    # return the response with the correct content type
    return Response(
        response_content,
        content_type=app.packages.simple.PYPI_INDEX_FORMAT_CONTENT_TYPE_MAPPING[
            index_format
        ],
    )

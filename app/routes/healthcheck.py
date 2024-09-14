from http import HTTPStatus

from flask import Blueprint, Response

healthcheck_bp = Blueprint("healthcheck", __name__, url_prefix="/healthcheck")


@healthcheck_bp.route("/")
def healthcheck_route():
    """
    Healtcheck route.
    """
    return Response("Healthy!", status=HTTPStatus.OK)

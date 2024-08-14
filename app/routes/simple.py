from app.app import flask_app


@flask_app.route("/simple/<string:package")
def simple_route(package: str):
    """
    This route is used to provide a simple index of a specific package
    """
    return f"Package: {package}"

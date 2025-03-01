from typing import Generator

import pytest
from flask import Flask

from app import constants

# this must be set before importing models
constants.IS_TESTING = True

from app.models.package import Package  # noqa: E402
from app.models.repository import Repository  # noqa: E402
from app.wsgi import create_app  # noqa: E402


@pytest.fixture
def repository() -> Repository:
    return Repository(
        slug="pypi",
        simple_url="https://pypi.org/simple",
        cache_minutes=10,
        timeout_seconds=10,
    )


@pytest.fixture
def package(repository: Repository) -> Package:
    return Package(repository=repository, name="vscode-task-runner")


@pytest.fixture
def app() -> Flask:
    return create_app()


@pytest.fixture
def app_request_context(app: Flask) -> Generator:
    with app.test_request_context():
        yield

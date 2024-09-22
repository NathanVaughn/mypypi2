from typing import Generator

import pytest
from flask import Flask

from app import constants

constants.IS_TESTING = True

if True:
    from app.models.package import Package
    from app.models.repository import Repository
    from app.wsgi import create_app


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

from typing import Generator

import pytest
from flask import Flask

from app.models.package import PackageSQL
from app.models.repository import RepositorySQL
from app.wsgi import create_app


@pytest.fixture
def repository() -> RepositorySQL:
    return RepositorySQL(
        slug="pypi",
        simple_url="https://pypi.org/simple",
        cache_minutes=10,
        timeout_seconds=10,
    )


@pytest.fixture
def package(repository: RepositorySQL) -> PackageSQL:
    return PackageSQL(repository=repository, name="vscode-task-runner")


@pytest.fixture
def app() -> Flask:
    return create_app(is_testing=True)


@pytest.fixture
def app_request_context(app: Flask) -> Generator:
    with app.test_request_context():
        yield

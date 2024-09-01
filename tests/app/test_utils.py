import app.utils
from app.models.repository import Repository


def test_log_package_name(
    repository: Repository,
) -> None:
    assert app.utils.log_package_name(repository, "test_package") == "pypi:test_package"

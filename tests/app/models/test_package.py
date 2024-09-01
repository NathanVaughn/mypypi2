import datetime

from freezegun import freeze_time

from app.models.package import Package


@freeze_time("2020-01-01 12:00:00")
def test_is_current(package: Package) -> None:
    """
    Test is_current attribute
    """
    package.last_updated = datetime.datetime(2020, 1, 1, 11, 59, 59)
    package.repository.cache_minutes = 10
    assert package.is_current is True

    package.last_updated = datetime.datetime(2020, 1, 1, 11, 49, 00)
    package.repository.cache_minutes = 10
    assert package.is_current is False


def test_repository_url(package: Package) -> None:
    """
    Test repository_url attribute
    """
    package.repository.simple_url = "https://example.com/simple/"
    package.name = "test_package"
    # trailing slash is important
    assert package.repository_url == "https://example.com/simple/test_package/"

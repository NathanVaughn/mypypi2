import pytest

import app.models.exceptions
import app.packages.simple
from app.models.enums import IndexFormat


@pytest.mark.parametrize(
    "given, expected",
    (
        ("black", "black"),
        ("BLACK", "black"),
        ("black.test", "black-test"),
        ("black_test", "black-test"),
    ),
)
def test_normalize_name(given: str, expected: str):
    """
    Test the package name normalization function.
    """
    assert app.packages.simple.normalize_name(given) == expected


@pytest.mark.parametrize(
    "given, expected",
    (
        ("0.5", 0.5),
        ("0.000", 0.0),
        ("1.000", 1.0),
        ("0.123", 0.123),
        ("1", 1),
        (".1", 0.1),
    ),
)
def test_validate_quality_pass(given: str, expected: float):
    """
    Test the quality value validation function with a valid value.
    """
    assert app.packages.simple.validate_quality(given) == expected


@pytest.mark.parametrize(
    "given", ("a", "0.0000", "1.2.3.4", "1.0001", "123", "1.001", "-1")
)
def test_validate_quality_fail(given: str):
    """
    Test the quality value validation function with an invalid value.
    """
    with pytest.raises(app.models.exceptions.InvalidQualityValue):
        app.packages.simple.validate_quality(given)


@pytest.mark.parametrize(
    "given_accept_header, given_query_format, expected",
    (
        # basic test
        ("text/html", None, IndexFormat.html),
        ("text/html", "text/html", IndexFormat.html),
        # ignoring no formats provideed
        ("bad format", None, None),
        ("bad format 1", "bad format 2", None),
        # use query format
        ("bad format", "text/html", IndexFormat.html),
        ("application/vnd.pypi.simple.v1+json", "text/html", IndexFormat.html),
        # equal sorting
        (
            "application/vnd.pypi.simple.v1+html,application/vnd.pypi.simple.v1+json",
            None,
            IndexFormat.html,
        ),
        # quality sorting
        (
            "application/vnd.pypi.simple.v1+json;q=0.5,application/vnd.pypi.simple.v1+html;q=0.1",
            None,
            IndexFormat.json,
        ),
        # bad quality value
        (
            "application/vnd.pypi.simple.v1+json;q=2,application/vnd.pypi.simple.v1+html;q=0.1",
            None,
            IndexFormat.html,
        ),
        # nothing provided
        (None, None, IndexFormat.html),
    ),
)
def test_determine_index_format(
    given_accept_header: str | None,
    given_query_format: str | None,
    expected: IndexFormat | None,
):
    """
    Test the quality value validation function with an invalid value.
    """
    assert (
        app.packages.simple.determine_index_format(
            given_accept_header, given_query_format
        )
        == expected
    )
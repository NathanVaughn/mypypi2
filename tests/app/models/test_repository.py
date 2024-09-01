from app.models.repository import Repository


def test_simple_url() -> None:
    """
    Test simple_url attribute
    """
    repository = Repository()
    repository.simple_url = "https://pypi.org/simple"
    assert repository.simple_url == "https://pypi.org/simple"

    # make sure trailing slashes are removed
    repository.simple_url = "https://pypi.org/simple/"
    assert repository.simple_url == "https://pypi.org/simple"

    # make sure trailing slashes are removed
    repository.simple_url = "https://pypi.org/simple////"
    assert repository.simple_url == "https://pypi.org/simple"

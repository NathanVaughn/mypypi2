"""
Standardize HTTP requests so we can include our user agent
"""

import requests

USER_AGENT = "MyPyPI2 (https://github.com/NathanVaughn/mypypi2)"


def stream(url: str) -> requests.Response:
    """
    Stream a URL
    """
    headers = {"User-Agent": USER_AGENT}
    return requests.get(url, stream=True, headers=headers)


def get(url: str, headers: dict[str, str], timeout: int) -> requests.Response:
    """
    Get a URL
    """
    headers["User-Agent"] = USER_AGENT
    return requests.get(url, headers=headers, timeout=timeout)

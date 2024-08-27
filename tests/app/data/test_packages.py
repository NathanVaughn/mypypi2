import pytest

import app.data.packages


@pytest.mark.parametrize(
    "filename, version",
    (
        ("lxml-1.3.4.win32-py2.4.exe", "1.3.4"),
        ("lxml-2.2.win32-py2.4.exe", "2.2"),
        ("greenlet-0.4.4.win-amd64-py2.6.msi", "0.4.4"),
        ("lxml-2.0-py2.4-win32.egg", "2.0"),
        ("coverage-4.0a5.tar.bz2", "4.0a5"),
        ("vscode_task_runner-1.2.0-py3-none-any.whl", "1.2.0"),
        ("vscode_task_runner-1.2.0.tar.gz", "1.2.0"),
        ("setuptools-0.6c4-1.src.rpm", "0.6c4"),
    ),
)
def test_parse_filename_version(filename: str, version: str) -> None:
    assert app.data.packages.parse_filename_version(filename) == version


@pytest.mark.parametrize(
    "given, hash",
    (
        ("sha256=1234", "1234"),
        ("sha256=1234abcd", "1234abcd"),
        ("1234", None),
    ),
)
def test_parse_sha256_hash(given: str, hash: str) -> None:
    assert app.data.packages.parse_sha256_hash(given) == hash

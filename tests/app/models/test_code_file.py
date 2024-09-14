import datetime

import pytest

from app.models.code_file import CodeFile
from app.models.code_file_hash import CodeFileHash
from app.models.package import Package


@pytest.mark.parametrize(
    "is_yanked, yanked_reason, expected",
    [
        (False, None, False),
        (True, None, True),
        (True, "reason", "reason"),
        (False, "reason", False),  # should not happen
    ],
)
def test_yanked(package: Package, is_yanked: bool, yanked_reason: str | None, expected: str | bool) -> None:
    """
    Test yanked attribute
    """
    code_file = CodeFile(
        package=package,
        is_yanked=is_yanked,
        yanked_reason=yanked_reason,
    )

    assert code_file.yanked == expected

def test_hash_value() -> None:
    """
    Test how hash_value is generated
    """
    # have to use an inherited class here, since the base class
    # doesn't have a foreign key

    # test no hashes
    code_file = CodeFile()
    assert code_file.hash_value is None

    # test one hash
    CodeFileHash(code_file=code_file, kind="sha256", value="1234567890abcdef")
    assert code_file.hash_value == "sha256=1234567890abcdef"

    # test multiple hashes
    CodeFileHash(code_file=code_file, kind="md5", value="abcdef1234567890")
    assert code_file.hash_value == "sha256=1234567890abcdef"


def test_download_url(package: Package, app_request_context: None) -> None:
    """
    Test download_url
    """
    # actually testing the exact value would be unfair,
    # so just making sure no error is raised and it looks reasonably correct

    filename = "vscode_task_runner-0.1.2-py3-none-any.whl"
    version = "0.1.2"

    package_file = CodeFile(package=package, filename=filename, version=version)

    assert package.repository.slug in package_file.download_url
    assert package.name in package_file.download_url
    assert filename in package_file.download_url


def test_html_download_url(package: Package, app_request_context: None) -> None:
    """
    Test how html_download_url is generated
    """
    # have to use an inherited class here, since the base class
    # doesn't have a foreign key

    filename = "vscode_task_runner-0.1.2-py3-none-any.whl"
    version = "0.1.2"

    # test no hashes
    code_file = CodeFile(package=package, filename=filename, version=version)
    assert package.repository.slug in code_file.html_download_url
    assert package.name in code_file.html_download_url
    assert filename in code_file.html_download_url
    assert "#" not in code_file.html_download_url

    # test one hash
    CodeFileHash(code_file=code_file, kind="sha256", value="1234567890abcdef")
    assert package.repository.slug in code_file.html_download_url
    assert package.name in code_file.html_download_url
    assert filename in code_file.html_download_url
    assert "#sha256=1234567890abcdef" in code_file.html_download_url

    # test multiple hashes
    CodeFileHash(code_file=code_file, kind="md5", value="abcdef1234567890")
    assert package.repository.slug in code_file.html_download_url
    assert package.name in code_file.html_download_url
    assert filename in code_file.html_download_url
    assert "#sha256=1234567890abcdef" in code_file.html_download_url


def test_update() -> None:
    """
    Test updates to a code file
    """
    file1 = CodeFile(filename="test.whl", version="1.0.0", upstream_url="https://example.com", requires_python=">=3.6", is_yanked=False, yanked_reason=None, size=12345, upload_time=datetime.datetime.now())
    CodeFileHash(code_file=file1, kind="sha256", value="1234567890abcdef")

    # update the file
    file2 = CodeFile(filename="other.whl", version="1.0.1", upstream_url="https://nathanv.me", requires_python=">=3.8", is_yanked=True, yanked_reason="reason", size=6789, upload_time=datetime.datetime(2021, 1, 1))
    CodeFileHash(code_file=file2, kind="md5", value="abcdef1234567890")

    file1.update(file2)
    # make sure filename is unchanged
    assert file1.filename == "test.whl"
    # make sure everything else is updated
    assert file1.version == "1.0.1"
    assert file1.upstream_url == "https://nathanv.me"
    assert file1.requires_python == ">=3.8"
    assert file1.is_yanked is True
    assert file1.yanked_reason == "reason"
    assert file1.size == 6789
    assert file1.upload_time == datetime.datetime(2021, 1, 1)
    assert file1.hashes[0].kind == "sha256"
    assert file1.hashes[0].value == "1234567890abcdef"
    assert file1.hashes[1].kind == "md5"
    assert file1.hashes[1].value == "abcdef1234567890"

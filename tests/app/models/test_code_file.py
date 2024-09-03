import datetime

import pytest

from app.models.code_file import CodeFileSQL
from app.models.code_file_hash import CodeFileHashSQL
from app.models.package import PackageSQL


@pytest.mark.parametrize(
    "is_yanked, yanked_reason, expected",
    [
        (False, None, False),
        (True, None, True),
        (True, "reason", "reason"),
        (False, "reason", False),  # should not happen
    ],
)
def test_yanked(package: PackageSQL, is_yanked: bool, yanked_reason: str | None, expected: str | bool) -> None:
    """
    Test yanked attribute
    """
    code_file = CodeFileSQL(
        package=package,
        is_yanked=is_yanked,
        yanked_reason=yanked_reason,
    )

    assert code_file.yanked == expected


def test_update() -> None:
    """
    Test updates to a code file
    """
    file1 = CodeFileSQL(filename="test.whl", version="1.0.0", upstream_url="https://example.com", requires_python=">=3.6", is_yanked=False, yanked_reason=None, size=12345, upload_time=datetime.datetime.now())
    CodeFileHashSQL(code_file=file1, kind="sha256", value="1234567890abcdef")

    # update the file
    file2 = CodeFileSQL(filename="other.whl", version="1.0.1", upstream_url="https://nathanv.me", requires_python=">=3.8", is_yanked=True, yanked_reason="reason", size=6789, upload_time=datetime.datetime(2021, 1, 1))
    CodeFileHashSQL(code_file=file2, kind="md5", value="abcdef1234567890")

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

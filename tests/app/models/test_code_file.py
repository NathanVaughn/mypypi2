import pytest

from app.models.code_file import CodeFile
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

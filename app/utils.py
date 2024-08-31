from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.repository import Repository


def log_package_name(
    repository: Repository,
    package_name: str,
    filename: str | None = None,
) -> str:
    """
    Generate a consistent log message for a package name
    """
    out = f"{repository.slug}:{package_name}"
    if filename:
        out += f"/{filename}"
    return out
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.repository import Repository  # pragma: no cover


def log_package_name(repository: Repository, package_name: str) -> str:
    """
    Generate a consistent log message for a package name
    """
    out = f"{repository.slug}:{package_name}"
    return out

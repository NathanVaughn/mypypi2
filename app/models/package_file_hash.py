from __future__ import annotations

from app.models.database import Base


class PackageFileHash(Base):
    """
    This model represents a content hash for a file associated with a package.
    Since the JSON API allows for files to have multiple hashes, we need a seperate
    table. This is a base model meant to inherited.
    """

    kind: str
    """
    Type of hash of the file
    """
    value: str
    """
    Hash of the file
    """

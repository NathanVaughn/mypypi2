

class PackageVersionFilename:
    _id: int
    package: str
    """
    Package name
    """
    version: str
    """
    Package version
    """
    filename: str
    """
    Package filename
    """
    upstream_url: str
    """
    Upstream URL where we can download this package
    """
    is_cached: bool
    """
    Have we already downloaded this package?
    """
    blake2b_256_hash: str
    """
    BLAKE2b-256 hash of the file
    """
    md5_hash: str
    """
    MD5 hash of the file
    """
    sha256_hash: str
    """
    SHA256 hash of the file
    """
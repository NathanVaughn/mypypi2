import dataclasses
import functools
import hashlib
import re
from urllib.parse import urljoin

import packaging.utils
import packaging.version

from app.constants import CONTENT_TYPE_HEADER_HTML
from app.models.enums import IndexFormat
from app.models.exceptions import InvalidQualityValue

# https://github.com/pypa/pip/blob/b989e6ef04810bbd4033a3683020bd4ddcbdb627/src/pip/_internal/models/link.py#L40
# From the Simple API spec:
# Repositories SHOULD choose a hash function from one of the ones guaranteed to be
# available via the hashlib module in the Python standard library
# (currently md5, sha1, sha224, sha256, sha384, sha512).
# The current recommendation is to use sha256.
# we're just validating the hash is allowable, so just use the import from hashlib
SUPPORTED_HASHES = hashlib.algorithms_guaranteed

PYPI_CONTENT_TYPE_PREFIX = "application/vnd.pypi.simple"

PYPI_CONTENT_TYPE_LEGACY = CONTENT_TYPE_HEADER_HTML
PYPI_CONTENT_TYPE_HTML_V1 = f"{PYPI_CONTENT_TYPE_PREFIX}.v1+html"
PYPI_CONTENT_TYPE_JSON_V1 = f"{PYPI_CONTENT_TYPE_PREFIX}.v1+json"
PYPI_CONTENT_TYPE_HTML_LATEST = f"{PYPI_CONTENT_TYPE_PREFIX}.latest+html"
PYPI_CONTENT_TYPE_JSON_LATEST = f"{PYPI_CONTENT_TYPE_PREFIX}.latest+json"


PYPI_CONTENT_TYPES = {
    PYPI_CONTENT_TYPE_LEGACY,
    PYPI_CONTENT_TYPE_HTML_V1,
    PYPI_CONTENT_TYPE_JSON_V1,
    PYPI_CONTENT_TYPE_HTML_LATEST,
    PYPI_CONTENT_TYPE_JSON_LATEST,
}
"""
List of all acceptable content types
"""

DEFAULT_CONTENT_TYPE = PYPI_CONTENT_TYPE_HTML_LATEST
"""
Basically every client can parse the HTML format, so we default to that.
"""

PYPI_INDEX_FORMAT_CONTENT_TYPE_MAPPING = {
    # this is so it works in a web browser
    IndexFormat.html: PYPI_CONTENT_TYPE_LEGACY,
    IndexFormat.json: PYPI_CONTENT_TYPE_JSON_V1,
}
"""
Mapping of index formats to the return contenty-type they should be served as.
"""

PYPI_CONTENT_TYPE_INDEX_FORMAT_MAPPING = {
    PYPI_CONTENT_TYPE_LEGACY: IndexFormat.html,
    PYPI_CONTENT_TYPE_HTML_V1: IndexFormat.html,
    PYPI_CONTENT_TYPE_JSON_V1: IndexFormat.json,
    PYPI_CONTENT_TYPE_HTML_LATEST: IndexFormat.html,
    PYPI_CONTENT_TYPE_JSON_LATEST: IndexFormat.json,
}
"""
Mapping of accpeted content types to the index format they represent.
"""


@dataclasses.dataclass
class ContentTypeSort:
    """
    Dataclass to hold a content type and its sorting value
    """

    content_type: str
    quality: float


@functools.cache
def normalize_name(package_name: str) -> str:
    """
    Normalize a package name
    """
    return re.sub(r"[-_.]+", "-", package_name).lower()


def validate_quality(quality: str) -> float:
    """
    Validate a quality value from the accept header.
    Raises a InvalidQualityValue if the quality is not valid.
    Needs to be a number between 0 and 1 with no more than
    3 decimal places.
    """

    if "." in quality and len(quality.split(".")[1]) > 3:
        raise InvalidQualityValue(f"Quality value {quality} has more than 3 decimal places")

    try:
        fquality = float(quality)
    except ValueError:
        raise InvalidQualityValue(f"Quality value {quality} is not a valid float")

    if not 0 <= fquality <= 1:
        raise InvalidQualityValue(f"Quality value {quality} is not between 0 and 1")

    return fquality


def determine_index_format(accept_header: str | None, format_query: str | None) -> IndexFormat | None:
    """
    Determine the content type based on the Accept header and the ?format query parameter.
    The ?format query parameter takes precedence over the Accept header.
    https://packaging.python.org/en/latest/specifications/simple-repository-api/#url-parameter

    The Accept header can be a comma-separated list of values, while the ?format query
    parameter can only be a single value.

    The Accept header can optionally be sorted by appending ;q= with a value between 0 and 1,
    with up to 3 decimal places. Higher value is preferred.

    This may return None if no supported content type was provided, per the
    index specification.
    """
    # build a sorted list of acceptable content types
    content_types: list[ContentTypeSort] = []

    # first, handle special case of accept header not being set
    if accept_header is None:
        # Default is */*, aka any content type
        accept_header = "*/*"

    if accept_header == "*/*":
        content_types.append(ContentTypeSort(DEFAULT_CONTENT_TYPE, 1))

    # parse the accept header
    for content_type in accept_header.split(","):
        # remove any extra spaces
        content_type = content_type.strip()
        # if the content type has a quality value, split it out
        if ";q=" in content_type:
            content_type, quality = content_type.split(";q=")

            # skip if the quality is invalid
            try:
                quality = validate_quality(quality)
            except InvalidQualityValue:
                continue

        # default 1.0 quality
        else:
            # https://packaging.python.org/en/latest/specifications/simple-repository-api/#version-format-selection
            quality = 1.0

        # skip unsupported content types
        if content_type in PYPI_CONTENT_TYPES:
            content_types.append(ContentTypeSort(content_type, quality))

    # if there is a format query, use that
    if format_query in PYPI_CONTENT_TYPES:
        content_types.append(ContentTypeSort(format_query, 999))

    # sort the content types by quality
    content_types.sort(key=lambda x: x.quality, reverse=True)

    # if there are no content types, return None
    if len(content_types) == 0:
        return None

    # return top pick
    return PYPI_CONTENT_TYPE_INDEX_FORMAT_MAPPING[content_types[0].content_type]


def parse_version(filename: str) -> str | None:
    """
    Take a filename and attempt to parse the version from it.
    Returns None if no version could be parsed.
    """
    if filename.endswith(".whl"):
        try:
            _, version, _, _ = packaging.utils.parse_wheel_filename(filename)
            return str(version)
        except packaging.utils.InvalidWheelFilename:
            return None

    elif filename.endswith(".zip") or filename.endswith(".tar.gz"):
        try:
            _, version = packaging.utils.parse_sdist_filename(filename)
            return str(version)
        except packaging.utils.InvalidSdistFilename:
            return None

    return None


def absoluify_url(base_url: str, href: str) -> str:
    """
    Take a URL and make it absolute based on a base URL.
    """
    return urljoin(base_url, href)

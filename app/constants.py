import os

# file extensions
METADATA_EXTENSION = ".metadata"

# keys
DATA_PREFIX = "data-"
# https://packaging.python.org/en/latest/specifications/simple-repository-api/#rename-dist-info-metadata-in-the-simple-api
METADATA_KEY_LEGACY = "dist-info-metadata"
METADATA_KEY_LEGACY2 = f"{DATA_PREFIX}{METADATA_KEY_LEGACY}"
# pypi still emits this one ^
METADATA_KEY = "core-metadata"

# HTTP headers
ACCEPT_HEADER = "Accept"
CONTENT_TYPE_HEADER = "Content-Type"
CONTENT_TYPE_HEADER_HTML = "text/html"
CONTENT_TYPE_HEADER_JSON = "application/json"

# number constants
MINUTES_TO_SECONDS = 60

# filesystem
ASSETS_DIRECTORY = os.path.join(os.path.dirname(__file__), "assets")

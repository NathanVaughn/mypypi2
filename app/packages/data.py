import datetime

import requests
from loguru import logger

import app.data.sql
import app.data.storage
from app.constants import CONTENT_TYPE_HEADER
from app.models.exceptions import IndexParsingError, IndexTimeoutError, PackageNotFound
from app.models.package import Package
from app.models.package_file import PackageFile
from app.models.repository import Repository
from app.packages.html import parse_simple_html
from app.packages.json import parse_simple_json
from app.packages.simple import (
    PYPI_CONTENT_TYPE_HTML_V1,
    PYPI_CONTENT_TYPE_INDEX_FORMAT_MAPPING,
    PYPI_CONTENT_TYPE_JSON_V1,
    PYPI_CONTENT_TYPE_LEGACY,
    IndexFormat,
)
from app.utils import log_package_name


def fetch_package_data(repository: Repository, package_name: str) -> Package:
    """
    Fetch package data.
    """
    logger.debug(f"Fetching package {
                 log_package_name(repository, package_name)}")
    package = Package(repository=repository, name=package_name)

    # make the request upstream
    url = package.repository_url
    content_types = [
        f"{PYPI_CONTENT_TYPE_JSON_V1};q=1",
        f"{PYPI_CONTENT_TYPE_HTML_V1};q=0.2",
        f"{PYPI_CONTENT_TYPE_LEGACY};q=0.01",
    ]
    headers = {"Accept": ",".join(content_types)}
    try:
        logger.info(f"Fetching {url}")
        response = requests.get(url, headers=headers, timeout=repository.timeout_seconds)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        # we need to handle this one specifically to pretend nothing happend
        raise IndexTimeoutError
    except Exception:
        # if we have any error, we need to raise a PackageNotFound
        raise PackageNotFound(package_name, repository_slug=repository.slug)

    # now, figure out how to parse the response.
    content_type = response.headers.get(CONTENT_TYPE_HEADER)

    # if content type is not in our mapping, raise an error
    if content_type not in PYPI_CONTENT_TYPE_INDEX_FORMAT_MAPPING:
        raise IndexParsingError(url)

    # parse the response
    index_format = PYPI_CONTENT_TYPE_INDEX_FORMAT_MAPPING[content_type]
    if index_format == IndexFormat.json:
        package.code_files = parse_simple_json(response.text, package)
    elif index_format == IndexFormat.html:
        package.code_files = parse_simple_html(response.text, package)

    # return our package object
    return package


def create_package_data(repository: Repository, package_name: str) -> Package:
    """
    Fetch package data for the first time.
    """
    logger.debug(f"Creating package {
                 log_package_name(repository, package_name)}")

    try:
        package = fetch_package_data(repository, package_name)
    except IndexTimeoutError:
        # since we have nothing to work with, raise a not found error
        raise PackageNotFound(package_name, repository_slug=repository.slug)

    # save the package to the database
    app.data.sql.save_package(package)
    return package


def update_package_data(repository: Repository, package: Package) -> Package:
    """
    Update the package data for a given package in our database
    """
    try:
        package = fetch_package_data(repository, package.name)
    except IndexTimeoutError:
        # pretend nothing happened
        return package

    # we need to compare a list of code files parsed to the ones we have already seen
    # We won't delete existing files, but only add new files.
    # Also need to rectify any changes. This will only include yanked, metadata, and hashes.

    # TODO: implement de-duping
    package.last_updated = datetime.datetime.now()
    app.data.sql.save_package(package)
    app.data.sql.save()

    return package


def get_package(repository_slug: str, package_name: str) -> Package:
    """
    Return a Package object for a given repository and package name.
    """
    # first try to find the repository
    repository = app.data.sql.get_repository_with_exception(repository_slug)

    # try to find the package in the database
    package = app.data.sql.get_package(repository, package_name)

    # if package is not in the database, we need to fetch it
    if package is None:
        package = create_package_data(repository, package_name)

    # or if the package is not current, we need to update it
    elif not package.is_current:
        package = update_package_data(repository, package)

    return package


def cache_package_file(package_file: PackageFile) -> None:
    """
    Cache a file
    """
    # skip if already cached
    if package_file.is_cached:
        return

    # actually cache the file
    app.data.storage.ActiveStorage.provider.cache_file(package_file)

    # update the database
    package_file.is_cached = True
    app.data.sql.save()


def get_package_file(repository_slug: str, package_name: str, filename: str) -> PackageFile:
    """
    Return a PackageFile object for a given repository, package name, and filename.
    """
    # first try to find the repository
    repository = app.data.sql.get_repository_with_exception(repository_slug)

    # try to find the package in the database
    # this shouldn't be the first time we're hearing of this package name
    # so if it is, we can raise an exception
    package = app.data.sql.get_package_with_exception(repository, package_name)

    # try to find the file in the database
    package_file = app.data.sql.get_package_file_with_exception(repository, package, filename)

    # if we haven't cached the file yet, do so now
    cache_package_file(package_file)

    return package_file

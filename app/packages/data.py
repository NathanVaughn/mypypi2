import datetime

import requests
from loguru import logger

import app.data.sql
import app.data.storage.active
import app.http
from app.constants import CONTENT_TYPE_HEADER
from app.models.code_file import CodeFile
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
from app.utils import time_this_context


def fetch_package_data(package: Package) -> list[CodeFile]:
    """
    Fetch package data.
    """
    logger.debug(f"Fetching package {package.log_name}")

    # make the request upstream
    url = package.repository_url
    content_types = [
        f"{PYPI_CONTENT_TYPE_JSON_V1};q=1",
        f"{PYPI_CONTENT_TYPE_HTML_V1};q=0.2",
        f"{PYPI_CONTENT_TYPE_LEGACY};q=0.01",
    ]
    headers = {"Accept": ",".join(content_types)}
    try:
        with time_this_context(f"Fetched {package.repository_url}"):
            response = app.http.get(url, headers=headers, timeout=package.repository.timeout_seconds)
            response.raise_for_status()
    except requests.exceptions.Timeout as e:
        # we need to handle this one specifically to pretend nothing happend
        raise IndexTimeoutError from e
    except Exception as e:
        # if we have any error, we need to raise a PackageNotFound
        raise PackageNotFound(package_name=package.name, repository_slug=package.repository.slug) from e

    # now, figure out how to parse the response.
    content_type = response.headers.get(CONTENT_TYPE_HEADER)

    # if content type is not in our mapping, raise an error
    if content_type not in PYPI_CONTENT_TYPE_INDEX_FORMAT_MAPPING:
        raise IndexParsingError(url)

    # parse the response
    index_format = PYPI_CONTENT_TYPE_INDEX_FORMAT_MAPPING[content_type]
    if index_format == IndexFormat.json:
        code_files = parse_simple_json(response.text, package)
    elif index_format == IndexFormat.html:
        code_files = parse_simple_html(response.text, package)
    else:
        raise IndexParsingError(url)

    # in some weird situations, (looking at you pytorch), we can have code files
    # with different URLs but the same filename.
    # In that situation, we discard any duplicates, preferring ones that occur first.
    unique_code_filenames = set()
    out_code_files: list[CodeFile] = []
    for code_file in code_files:
        # if we have already seen this filename, skip it
        if code_file.filename in unique_code_filenames:
            logger.warning(
                f"Discarding duplicate code file {
                    code_file.filename
                }. This should not happen. The upstream registry is not configured properly."
            )
            continue

        unique_code_filenames.add(code_file.filename)
        out_code_files.append(code_file)

    return out_code_files


def create_package_data(repository: Repository, package_name: str) -> Package:
    """
    Fetch package data for the first time.
    """
    package = Package(repository=repository, name=package_name)
    logger.debug(f"Creating package {package.log_name}")

    try:
        package.code_files = fetch_package_data(package)
    except IndexTimeoutError:
        # since we have nothing to work with, raise a not found error
        raise PackageNotFound(package_name=package.name, repository_slug=repository.slug)

    # set the package for each code file
    for code_file in package.code_files:
        code_file.package = package
        if code_file.metadata_file:
            code_file.metadata_file.package = package

    # save the new package to the database
    with time_this_context(f"Saved {package.child_count} new rows for package {package.log_name}"):
        app.data.sql.session_save(package)
    return package


def update_package_data(repository: Repository, package: Package) -> Package:
    """
    Update the package data for a given package in our database
    """
    # first, we need to get the existing code files
    old_code_files_dict = {code_file.filename: code_file for code_file in package.code_files}
    old_code_files_filenames_set = set(old_code_files_dict.keys())

    try:
        new_code_files = fetch_package_data(package)
    except IndexTimeoutError:
        # pretend nothing happened
        return package

    # we need to compare a list of code files parsed to the ones we have already seen
    # We won't delete existing files, but only add new files.
    # Also need to rectify any changes. This will only include yanked, metadata, and hashes.
    new_code_files_dict = {code_file.filename: code_file for code_file in new_code_files}

    to_save_code_files: list[CodeFile] = []
    # add new code files
    for new_code_file_filename, new_code_file in new_code_files_dict.items():
        if new_code_file_filename not in old_code_files_filenames_set:
            to_save_code_files.append(new_code_file)
        else:
            # rectify any changes
            old_code_files_dict[new_code_file_filename].update(new_code_file)

    # set the package for each code file
    for code_file in to_save_code_files:
        code_file.package = package
        if code_file.metadata_file:
            code_file.metadata_file.package = package

    # also have to update existing code files list
    package.code_files += to_save_code_files

    logger.debug(f"Saving {len(to_save_code_files)} new code files for package {package.log_name}")
    package.last_updated = datetime.datetime.now()
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
    app.data.storage.active.StorageDriver.cache_file(package_file)

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

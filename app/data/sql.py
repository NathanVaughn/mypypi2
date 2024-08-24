import datetime

from app.models.database import db
from app.models.package_update import PackageUpdate
from app.models.package_version_filename import PackageVersionFilename
from app.models.repository import Repository
from app.models.url_cache import URLCache


def lookup_repository(repository_slug: str) -> Repository | None:
    """
    Lookup a Repository object given the slug
    """
    return db.session.execute(
        db.select(Repository).where(Repository.slug == repository_slug)
    ).scalar_one_or_none()


def lookup_package_version_filename(
    repository_slug: str, filename: str
) -> PackageVersionFilename | None:
    """
    Lookup a PackageVersionFilename object given the filename
    """
    return db.session.execute(
        db.select(PackageVersionFilename)
        .join(PackageVersionFilename.repository)
        .where(
            PackageVersionFilename.filename == filename,
            Repository.slug == repository_slug,
        )
    ).scalar_one_or_none()


def lookup_package_update(repository_slug: str, package: str) -> PackageUpdate | None:
    """
    Lookup a PackageUpdate object given the package name
    """
    return db.session.execute(
        db.select(PackageUpdate)
        .join(PackageUpdate.repository)
        .where(PackageUpdate.package == package, Repository.slug == repository_slug)
    ).scalar_one_or_none()


def lookup_url_cache(repository_slug: str, url: str) -> URLCache | None:
    """
    Lookup a URLCache object given the url
    """
    return db.session.execute(
        db.select(URLCache)
        .join(URLCache.repository)
        .where(URLCache.url == url, Repository.slug == repository_slug)
    ).scalar_one_or_none()


def get_package_version_filenames(
    repository_slug: str, package: str
) -> list[PackageVersionFilename]:
    """
    Return a list of PackageVersionFilename objects for a given package
    """
    return (
        db.session.execute(
            db.select(PackageVersionFilename)
            .join(PackageVersionFilename.repository)
            .where(
                PackageVersionFilename.package == package,
                Repository.slug == repository_slug,
            )
        )
        .scalars()
        .all()
    )  # type: ignore


def update_package_last_updated(repository_slug: str, package: str) -> None:
    """
    Update the package data for a given package in our database
    """
    # record the last time we've updated this package
    package_update = db.session.execute(
        db.select(PackageUpdate)
        .join(PackageUpdate.repository)
        .where(PackageUpdate.package == package, Repository.slug == repository_slug)
    ).scalar_one_or_none()

    if package_update is None:
        # create a new record if this is the first time
        repository = lookup_repository(repository_slug)
        package_update = PackageUpdate(
            repository=repository, package=package, last_updated=datetime.datetime.now()
        )
        db.session.add(package_update)
    else:
        package_update.last_updated = datetime.datetime.now()

    db.session.commit()

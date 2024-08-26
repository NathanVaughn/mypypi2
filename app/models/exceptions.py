class RepositoryNotFound(Exception):
    def __init__(self, repository_slug: str):
        self.repository_slug = repository_slug
        super().__init__(f"Repository {repository_slug} not found")


class PackageFileNotFound(Exception):
    def __init__(self, repository_slug: str, package_name: str, filename: str):
        self.repository_slug = repository_slug
        self.package_name = package_name
        self.filename = filename
        super().__init__(f"Package file {filename} not found in {
            repository_slug}/{package_name}")

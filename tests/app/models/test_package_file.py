from app.models.code_file import CodeFile
from app.models.code_file_hash import CodeFileHash
from app.models.package import Package
from app.models.package_file import PackageFile


def test_version_text() -> None:
    """
    Test how version_text is generated
    """
    package_file = PackageFile(version=None)
    assert package_file.version_text == "UNKNOWN"

    package_file = PackageFile(version="1.2.3")
    assert package_file.version_text == "1.2.3"


def test_hash_value() -> None:
    """
    Test how hash_value is generated
    """
    # have to use an inherited class here, since the base class
    # doesn't have a foreign key

    # test no hashes
    code_file = CodeFile()
    assert code_file.hash_value is None

    # test one hash
    CodeFileHash(code_file=code_file, kind="sha256", value="1234567890abcdef")
    assert code_file.hash_value == "sha256=1234567890abcdef"

    # test multiple hashes
    CodeFileHash(code_file=code_file, kind="md5", value="abcdef1234567890")
    assert code_file.hash_value == "sha256=1234567890abcdef"


def test_hashes_dict() -> None:
    """
    Test how hashes_dict is generated
    """
    # have to use an inherited class here, since the base class
    # doesn't have a foreign key

    # test no hashes
    code_file = CodeFile()
    assert code_file.hashes_dict == {}

    # test one hash
    CodeFileHash(code_file=code_file, kind="sha256", value="1234567890abcdef")
    assert code_file.hashes_dict == {"sha256": "1234567890abcdef"}

    # test multiple hashes
    CodeFileHash(code_file=code_file, kind="md5", value="abcdef1234567890")
    assert code_file.hashes_dict == {"sha256": "1234567890abcdef", "md5": "abcdef1234567890"}


def test_download_url(package: Package, app_request_context: None) -> None:
    """
    Test download_url
    """
    # actually testing the exact value would be unfair,
    # so just making sure no error is raised and it looks reasonably correct

    filename = "vscode_task_runner-0.1.2-py3-none-any.whl"
    version = "0.1.2"

    package_file = CodeFile(package=package, filename=filename, version=version)

    assert package.repository.slug in package_file.download_url
    assert package.name in package_file.download_url
    assert filename in package_file.download_url


def test_html_download_url(package: Package, app_request_context: None) -> None:
    """
    Test how html_download_url is generated
    """
    # have to use an inherited class here, since the base class
    # doesn't have a foreign key

    filename = "vscode_task_runner-0.1.2-py3-none-any.whl"
    version = "0.1.2"

    # test no hashes
    code_file = CodeFile(package=package, filename=filename, version=version)
    assert package.repository.slug in code_file.html_download_url
    assert package.name in code_file.html_download_url
    assert filename in code_file.html_download_url
    assert "#" not in code_file.html_download_url

    # test one hash
    CodeFileHash(code_file=code_file, kind="sha256", value="1234567890abcdef")
    assert package.repository.slug in code_file.html_download_url
    assert package.name in code_file.html_download_url
    assert filename in code_file.html_download_url
    assert "#sha256=1234567890abcdef" in code_file.html_download_url

    # test multiple hashes
    CodeFileHash(code_file=code_file, kind="md5", value="abcdef1234567890")
    assert package.repository.slug in code_file.html_download_url
    assert package.name in code_file.html_download_url
    assert filename in code_file.html_download_url
    assert "#sha256=1234567890abcdef" in code_file.html_download_url

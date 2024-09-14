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

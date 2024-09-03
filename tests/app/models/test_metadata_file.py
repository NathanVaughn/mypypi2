from app.models.metadata_file import MetadataFileSQL
from app.models.metadata_file_hash import MetadataFileHashSQL


def test_update() -> None:
    """
    Test updates to a metadata file
    """
    file1 = MetadataFileSQL(filename="test.metadata", version="1.0.0", upstream_url="https://example.com")
    MetadataFileHashSQL(metadata_file=file1, kind="sha256", value="1234567890abcdef")

    # update the file
    file2 = MetadataFileSQL(filename="other.metadata", version="1.0.1", upstream_url="https://nathanv.me")
    MetadataFileHashSQL(metadata_file=file2, kind="md5", value="abcdef1234567890")

    file1.update(file2)
    # make sure filename is unchanged
    assert file1.filename == "test.metadata"
    # make sure everything else is updated
    assert file1.version == "1.0.1"
    assert file1.upstream_url == "https://nathanv.me"
    assert file1.hashes[0].kind == "sha256"
    assert file1.hashes[0].value == "1234567890abcdef"
    assert file1.hashes[1].kind == "md5"
    assert file1.hashes[1].value == "abcdef1234567890"

import datetime

import app.packages.json
from app.models.package import Package


def test__parse_single_record1(package: Package) -> None:
    """
    Test the parsing of a single record. Main test on a real example.
    """
    record = {
        "core-metadata": {"sha256": "4a7687e223ae9c52899b004c8ce445bb8e5e7a749adfb1355da94fd32ff46527"},
        "data-dist-info-metadata": {"sha256": "4a7687e223ae9c52899b004c8ce445bb8e5e7a749adfb1355da94fd32ff46527"},
        "filename": "vscode_task_runner-0.1.2-py3-none-any.whl",
        "hashes": {"sha256": "9f046728d31a5b09b4463b04ba5370650f42874eb0a7446745f3e3477cb3b8f0"},
        "requires-python": ">=3.10,<4.0",
        "size": 14920,
        "upload-time": "2023-05-29T18:23:41.200050Z",
        "url": "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl",
        "yanked": False,
    }

    result = app.packages.json._parse_single_record(record=record, package=package)

    assert result.filename == "vscode_task_runner-0.1.2-py3-none-any.whl"
    assert result.upstream_url == "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl"
    assert result.requires_python == ">=3.10,<4.0"
    assert result.is_yanked is False
    assert result.yanked_reason is None
    assert result.size == 14920
    assert result.upload_time == datetime.datetime(2023, 5, 29, 18, 23, 41, 200050, tzinfo=datetime.timezone.utc)
    assert result.version == "0.1.2"
    assert result.hashes[0].kind == "sha256"
    assert result.hashes[0].value == "9f046728d31a5b09b4463b04ba5370650f42874eb0a7446745f3e3477cb3b8f0"
    assert result.metadata_file.filename == "vscode_task_runner-0.1.2-py3-none-any.whl.metadata"
    assert result.metadata_file.upstream_url == "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl.metadata"
    assert result.metadata_file.version == "0.1.2"
    assert result.metadata_file.hashes[0].kind == "sha256"
    assert result.metadata_file.hashes[0].value == "4a7687e223ae9c52899b004c8ce445bb8e5e7a749adfb1355da94fd32ff46527"

    assert len(result.hashes) == 1
    assert len(result.metadata_file.hashes) == 1


def test__parse_single_record2(package: Package) -> None:
    """
    Test the parsing of a single record.
    Tests: Having a yanked reason, missing python requires, legacy metadata key only, and multiple hashes.
    """
    record = {
        "dist-info-metadata": {
            "sha256": "4a7687e223ae9c52899b004c8ce445bb8e5e7a749adfb1355da94fd32ff46527",
            "md5": "6c676d39a1250b34da0e2df2ec4a71c9",
        },
        "filename": "vscode_task_runner-0.1.2-py3-none-any.whl",
        "hashes": {
            "sha256": "9f046728d31a5b09b4463b04ba5370650f42874eb0a7446745f3e3477cb3b8f0",
            "md5": "0e0499d13614de61617d94f23410da6c",
        },
        "url": "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl",
        "yanked": "This was yanked because of reasons",
    }

    result = app.packages.json._parse_single_record(record=record, package=package)

    assert result.filename == "vscode_task_runner-0.1.2-py3-none-any.whl"
    assert result.upstream_url == "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl"
    assert result.requires_python is None
    assert result.is_yanked is True
    assert result.yanked_reason == "This was yanked because of reasons"
    assert result.version == "0.1.2"
    assert result.hashes[0].kind == "sha256"
    assert result.hashes[0].value == "9f046728d31a5b09b4463b04ba5370650f42874eb0a7446745f3e3477cb3b8f0"
    assert result.hashes[1].kind == "md5"
    assert result.hashes[1].value == "0e0499d13614de61617d94f23410da6c"
    assert result.metadata_file.filename == "vscode_task_runner-0.1.2-py3-none-any.whl.metadata"
    assert result.metadata_file.upstream_url == "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl.metadata"
    assert result.metadata_file.version == "0.1.2"
    assert result.metadata_file.hashes[0].kind == "sha256"
    assert result.metadata_file.hashes[0].value == "4a7687e223ae9c52899b004c8ce445bb8e5e7a749adfb1355da94fd32ff46527"
    assert result.metadata_file.hashes[1].kind == "md5"
    assert result.metadata_file.hashes[1].value == "6c676d39a1250b34da0e2df2ec4a71c9"

    assert len(result.hashes) == 2
    assert len(result.metadata_file.hashes) == 2


def test__parse_single_record3(package: Package) -> None:
    """
    Test the parsing of a single record.
    Tests: Yanked with no reason, pypi-only metadata key, and unsupported hash types
    """
    record = {
        "data-dist-info-metadata": {"notreal": "4a7687e223ae9c52899b004c8ce445bb8e5e7a749adfb1355da94fd32ff46527"},
        "filename": "vscode_task_runner-0.1.2-py3-none-any.whl",
        "hashes": {"notreal": "9f046728d31a5b09b4463b04ba5370650f42874eb0a7446745f3e3477cb3b8f0"},
        "url": "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl",
        "yanked": True,
    }

    result = app.packages.json._parse_single_record(record=record, package=package)

    assert result.filename == "vscode_task_runner-0.1.2-py3-none-any.whl"
    assert result.upstream_url == "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl"
    assert result.requires_python is None
    assert result.is_yanked is True
    assert result.yanked_reason is None
    assert result.version == "0.1.2"
    assert result.metadata_file.filename == "vscode_task_runner-0.1.2-py3-none-any.whl.metadata"
    assert result.metadata_file.upstream_url == "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl.metadata"
    assert result.metadata_file.version == "0.1.2"

    assert len(result.hashes) == 0
    assert len(result.metadata_file.hashes) == 0


def test__parse_single_record4(package: Package) -> None:
    """
    Test the parsing of a single record, bare minimum.
    Tests: No metadata or hashes
    """
    record = {
        "filename": "vscode_task_runner-0.1.2-py3-none-any.whl",
        "hashes": {},
        "url": "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl",
    }

    result = app.packages.json._parse_single_record(record=record, package=package)

    assert result.filename == "vscode_task_runner-0.1.2-py3-none-any.whl"
    assert result.upstream_url == "https://files.pythonhosted.org/packages/9f/cd/a21a34074a00154b61d981218bb767a8bd130e76d08f65d64b2a3a18547a/vscode_task_runner-0.1.2-py3-none-any.whl"
    assert result.requires_python is None
    assert result.is_yanked is False
    assert result.yanked_reason is None
    assert result.version == "0.1.2"
    assert result.metadata_file is None

    assert len(result.hashes) == 0

from io import BytesIO
from unittest.mock import MagicMock

import pytest

boto3 = pytest.importorskip("boto3")
s3 = pytest.importorskip("pakkenellik.aws.s3")


def test_build_s3_key_strips_duplicate_slashes() -> None:
    assert s3.build_s3_key("/folder/", "report", "/latest.json") == (
        "folder/report/latest.json"
    )


def test_build_public_url_joins_base_url_and_key() -> None:
    assert s3.build_public_url("https://example.com/", "/data/file.json") == (
        "https://example.com/data/file.json"
    )


def test_put_text_object_sets_headers_and_metadata(monkeypatch) -> None:
    client = MagicMock()
    monkeypatch.setattr(s3.boto3, "client", MagicMock(return_value=client))

    result = s3.put_text_object(
        "bucket",
        "key.json",
        '{"ok": true}',
        content_type="application/json",
        cache_control="max-age=30",
        metadata={"surrogate-key": "dataset"},
    )

    assert result == "key.json"
    client.put_object.assert_called_once_with(
        Bucket="bucket",
        Key="key.json",
        Body=b'{"ok": true}',
        ContentType="application/json",
        CacheControl="max-age=30",
        Metadata={"surrogate-key": "dataset"},
    )


def test_publish_to_s3_uploads_latest_and_archive_without_acl(monkeypatch) -> None:
    put_text_object = MagicMock()
    monkeypatch.setattr(s3, "put_text_object", put_text_object)

    result = s3.publish_to_s3(
        bucket="bucket",
        folder="exports",
        report_name="numbers",
        report_date="2026-06-25",
        data="{}",
        surrogate_key="numbers",
    )

    assert result == [
        "exports/numbers/numbers_latest.json",
        "exports/numbers/archive/2026-06-25_numbers.json",
    ]
    assert put_text_object.call_count == 2
    first_call = put_text_object.call_args_list[0]
    assert first_call.kwargs["metadata"] == {
        "surrogate-key": "numbers",
        "surrogate-control": s3.DEFAULT_SURROGATE_CONTROL,
    }
    assert "ACL" not in first_call.kwargs


def test_publish_to_s3_can_skip_archive(monkeypatch) -> None:
    put_text_object = MagicMock()
    monkeypatch.setattr(s3, "put_text_object", put_text_object)

    result = s3.publish_to_s3(
        "bucket",
        "exports",
        "numbers",
        "2026-06-25",
        "{}",
        skip_archive=True,
    )

    assert result == ["exports/numbers/numbers_latest.json"]
    put_text_object.assert_called_once()


def test_save_to_s3_uses_managed_upload_with_extra_args(monkeypatch) -> None:
    client = MagicMock()
    filecontent = BytesIO(b"hello")
    monkeypatch.setattr(s3.boto3, "client", MagicMock(return_value=client))

    result = s3.save_to_s3(
        "bucket",
        "file.txt",
        filecontent,
        content_type="text/plain",
        cache_control="max-age=60",
        metadata={"source": "test"},
    )

    assert result == "file.txt"
    client.upload_fileobj.assert_called_once_with(
        Fileobj=filecontent,
        Bucket="bucket",
        Key="file.txt",
        ExtraArgs={
            "ContentType": "text/plain",
            "CacheControl": "max-age=60",
            "Metadata": {"source": "test"},
        },
    )


def test_get_matching_s3_keys_uses_paginator_and_suffix_filter(monkeypatch) -> None:
    paginator = MagicMock()
    paginator.paginate.return_value = [
        {
            "Contents": [
                {"Key": "exports/a.json"},
                {"Key": "exports/a.csv"},
            ]
        },
        {"Contents": [{"Key": "exports/b.json"}]},
    ]
    client = MagicMock()
    client.get_paginator.return_value = paginator
    monkeypatch.setattr(s3.boto3, "client", MagicMock(return_value=client))

    result = list(s3.get_matching_s3_keys("bucket", prefix="exports/", suffix=".json"))

    assert result == ["exports/a.json", "exports/b.json"]
    client.get_paginator.assert_called_once_with("list_objects_v2")
    paginator.paginate.assert_called_once_with(Bucket="bucket", Prefix="exports/")

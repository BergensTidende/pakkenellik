from typing import BinaryIO, Generator, Optional

import boto3

"""
Utils for working with S3 from notebooks.
"""

DEFAULT_CACHE_CONTROL = "max-age=60"
DEFAULT_SURROGATE_CONTROL = "max-age=1800"


def build_s3_key(*parts: str) -> str:
    """Build an S3 key from path parts without duplicate slashes."""
    return "/".join(part.strip("/") for part in parts if part.strip("/"))


def build_public_url(public_base_url: str, key: str) -> str:
    """Build a public URL from a base URL and S3 key."""
    return f"{public_base_url.rstrip('/')}/{key.lstrip('/')}"


def put_text_object(
    bucket: str,
    key: str,
    data: str,
    *,
    content_type: str = "application/json",
    cache_control: Optional[str] = DEFAULT_CACHE_CONTROL,
    metadata: Optional[dict[str, str]] = None,
) -> str:
    """Upload text content to S3 and return the uploaded key."""
    extra_args: dict[str, object] = {
        "Bucket": bucket,
        "Key": key,
        "Body": data.encode("utf-8"),
        "ContentType": content_type,
    }
    if cache_control is not None:
        extra_args["CacheControl"] = cache_control
    if metadata:
        extra_args["Metadata"] = metadata

    boto3.client("s3").put_object(**extra_args)
    return key


def publish_to_s3(
    bucket: str,
    folder: str,
    report_name: str,
    report_date: str,
    data: str,
    content_type: str = "application/json",
    file_extension: str = "json",
    skip_archive: bool = False,
    public_base_url: Optional[str] = None,
    cache_control: Optional[str] = DEFAULT_CACHE_CONTROL,
    surrogate_key: Optional[str] = None,
    surrogate_control: Optional[str] = DEFAULT_SURROGATE_CONTROL,
) -> list[str]:
    """Publish a latest object and optionally an archived object to S3.

    Access is controlled by bucket policy/IAM, not object ACLs.
    """
    metadata = {}
    if surrogate_key is not None:
        metadata["surrogate-key"] = surrogate_key
    if surrogate_control is not None:
        metadata["surrogate-control"] = surrogate_control

    keys = [build_s3_key(folder, report_name, f"{report_name}_latest.{file_extension}")]
    if not skip_archive:
        keys.append(
            build_s3_key(
                folder,
                report_name,
                "archive",
                f"{report_date}_{report_name}.{file_extension}",
            )
        )

    for key in keys:
        put_text_object(
            bucket,
            key,
            data,
            content_type=content_type,
            cache_control=cache_control,
            metadata=metadata or None,
        )
        if public_base_url is not None:
            print(build_public_url(public_base_url, key))

    return keys


def save_to_s3(
    bucket: str,
    key: str,
    filecontent: BinaryIO,
    *,
    content_type: Optional[str] = None,
    cache_control: Optional[str] = None,
    metadata: Optional[dict[str, str]] = None,
) -> str:
    """Save a binary file-like object to S3 and return the uploaded key."""
    extra_args: dict[str, object] = {}
    if content_type is not None:
        extra_args["ContentType"] = content_type
    if cache_control is not None:
        extra_args["CacheControl"] = cache_control
    if metadata:
        extra_args["Metadata"] = metadata

    upload_kwargs: dict[str, object] = {
        "Fileobj": filecontent,
        "Bucket": bucket,
        "Key": key,
    }
    if extra_args:
        upload_kwargs["ExtraArgs"] = extra_args

    boto3.client("s3").upload_fileobj(**upload_kwargs)
    return key


def get_matching_s3_keys(
    bucket: str,
    prefix: str = "",
    suffix: str = "",
) -> Generator[str, None, None]:
    """Generate keys in an S3 bucket matching prefix and suffix."""
    paginator = boto3.client("s3").get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

    for page in page_iterator:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(suffix):
                yield key

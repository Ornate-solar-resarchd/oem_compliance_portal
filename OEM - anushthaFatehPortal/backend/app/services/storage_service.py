"""
StorageService — MinIO / S3-compatible object storage abstraction.
"""
from __future__ import annotations

import asyncio
import io
import re
import uuid
from datetime import datetime, timezone
from functools import lru_cache

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import settings

_MAX_DATASHEET_BYTES = 50 * 1024 * 1024   # 50 MB
_MAX_DOCUMENT_BYTES = 100 * 1024 * 1024    # 100 MB

_ALLOWED_BUCKETS = frozenset({
    settings.MINIO_BUCKET_DATASHEETS,
    settings.MINIO_BUCKET_DOCUMENTS,
})


@lru_cache(maxsize=1)
def _s3_client():
    endpoint = settings.MINIO_ENDPOINT
    scheme = "https" if settings.MINIO_SECURE else "http"
    return boto3.client(
        "s3",
        endpoint_url=f"{scheme}://{endpoint}",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        config=BotoConfig(signature_version="s3v4"),
        region_name="us-east-1",
    )


def _sanitize(name: str) -> str:
    """Strip path-traversal sequences and collapse whitespace."""
    name = name.replace("..", "").replace("/", "_").replace("\\", "_")
    return re.sub(r"\s+", "_", name).strip("_") or "file"


class StorageService:
    """Async wrapper around boto3 S3 operations."""

    def _validate_bucket(self, bucket: str) -> None:
        if bucket not in _ALLOWED_BUCKETS:
            raise ValueError(f"Bucket '{bucket}' is not allowed")

    def _max_size(self, bucket: str) -> int:
        if bucket == settings.MINIO_BUCKET_DATASHEETS:
            return _MAX_DATASHEET_BYTES
        return _MAX_DOCUMENT_BYTES

    async def upload_file(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        self._validate_bucket(bucket)
        if len(data) > self._max_size(bucket):
            raise ValueError(
                f"File exceeds max size of {self._max_size(bucket) // (1024*1024)} MB"
            )
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: _s3_client().put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            ),
        )
        return key

    async def download_file(self, bucket: str, key: str) -> bytes:
        self._validate_bucket(bucket)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: _s3_client().get_object(Bucket=bucket, Key=key),
        )
        return response["Body"].read()

    async def get_presigned_url(
        self, bucket: str, key: str, expires_seconds: int = 3600
    ) -> str:
        self._validate_bucket(bucket)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: _s3_client().generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_seconds,
            ),
        )

    async def delete_file(self, bucket: str, key: str) -> bool:
        self._validate_bucket(bucket)
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: _s3_client().delete_object(Bucket=bucket, Key=key),
            )
            return True
        except ClientError:
            return False

    async def file_exists(self, bucket: str, key: str) -> bool:
        self._validate_bucket(bucket)
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: _s3_client().head_object(Bucket=bucket, Key=key),
            )
            return True
        except ClientError:
            return False

    @staticmethod
    def generate_key(prefix: str, filename: str) -> str:
        now = datetime.now(timezone.utc)
        safe = _sanitize(filename)
        return f"{prefix}/{now:%Y}/{now:%m}/{uuid.uuid4().hex[:12]}-{safe}"

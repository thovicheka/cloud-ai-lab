import boto3
import pytest
from moto import mock_aws

from lab import storage

ENDPOINT = "https://fake-account.r2.cloudflarestorage.com"


@pytest.fixture
def r2(monkeypatch):
    """An empty in-memory bucket behind an R2-style endpoint: no network, no real keys."""
    monkeypatch.setenv("R2_ENDPOINT_URL", ENDPOINT)
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("R2_BUCKET", "test-bucket")
    monkeypatch.setenv("MOTO_S3_CUSTOM_ENDPOINTS", ENDPOINT)  # else moto lets R2 URLs through
    storage.client.cache_clear()
    with mock_aws():
        boto3.client("s3", endpoint_url=ENDPOINT, region_name="us-east-1").create_bucket(
            Bucket="test-bucket"
        )
        yield
    storage.client.cache_clear()

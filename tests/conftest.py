import io
import json

import boto3
import pytest
from moto import mock_aws

from lab import notify, storage

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


TOKEN = "123456:FAKE-TOKEN-must-never-be-printed"


@pytest.fixture
def telegram(monkeypatch):
    """Configure fake credentials and record every request instead of sending it."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN)
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    sent = []

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request, timeout):
        sent.append({"url": request.full_url, **json.loads(request.data)})
        return Response(b'{"ok": true}')

    monkeypatch.setattr(notify.urllib.request, "urlopen", fake_urlopen)
    return sent

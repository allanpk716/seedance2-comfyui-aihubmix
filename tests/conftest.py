import pytest


@pytest.fixture
def mock_api_key():
    """Return a test API key string."""
    return "test-api-key-12345"


@pytest.fixture
def mock_video_response():
    """Return a dict mimicking a completed AIHubMix API response."""
    return {
        "id": "vid_test123",
        "status": "completed",
        "progress": 100,
        "video_url": "https://example.com/video.mp4",
    }


@pytest.fixture
def mock_pending_response():
    """Return a dict mimicking an in-progress AIHubMix API response."""
    return {
        "status": "in_progress",
        "progress": 50,
    }


@pytest.fixture
def mock_failed_response():
    """Return a dict mimicking a failed AIHubMix API response."""
    return {
        "status": "failed",
        "error": {"message": "Test error"},
    }

import os
import tempfile

import cv2
import numpy as np
import pytest
from unittest.mock import MagicMock, patch


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
def mock_i2v_response():
    """Return a dict mimicking a completed I2V AIHubMix API response."""
    return {
        "id": "vid_i2v_test",
        "status": "completed",
        "video_url": "https://example.com/i2v_video.mp4",
    }


@pytest.fixture
def mock_extend_response():
    """Return a dict mimicking a completed Extend AIHubMix API response."""
    return {
        "id": "vid_ext_test",
        "status": "completed",
        "video_url": "https://example.com/extend_video.mp4",
    }


@pytest.fixture
def mock_failed_response():
    """Return a dict mimicking a failed AIHubMix API response."""
    return {
        "status": "failed",
        "error": {"message": "Test error"},
    }


@pytest.fixture
def sample_video_url():
    """Return a fake video URL for testing."""
    return "https://example.com/test_video.mp4"


@pytest.fixture
def mock_video_bytes(tmp_path):
    """Create a minimal valid MP4 video and return its bytes.

    Uses cv2.VideoWriter to produce a tiny 4-frame, 16x16 pixel video.
    Each frame has distinguishable brightness levels for testing.
    """
    video_path = str(tmp_path / "test_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(video_path, fourcc, 10.0, (16, 16))
    for i in range(4):
        frame = np.zeros((16, 16, 3), dtype=np.uint8)
        frame[i * 4:(i + 1) * 4, :, :] = i * 60
        writer.write(frame)
    writer.release()

    with open(video_path, "rb") as f:
        video_bytes = f.read()
    return video_bytes


@pytest.fixture
def mock_folder_paths(tmp_path):
    """Mock the ComfyUI folder_paths module so get_output_directory returns a temp dir."""
    mock_module = MagicMock()
    mock_module.get_output_directory.return_value = str(tmp_path)
    with patch.dict("sys.modules", {"folder_paths": mock_module}):
        yield mock_module


@pytest.fixture
def sample_image_tensor():
    """Return a random ComfyUI IMAGE tensor (1, 32, 32, 3) for I2V testing convenience."""
    import torch
    return torch.rand(1, 32, 32, 3)

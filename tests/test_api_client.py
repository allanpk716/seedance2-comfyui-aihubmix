"""Unit tests for api_client module with mocked HTTP responses."""
from unittest.mock import patch, MagicMock

import requests

from api_client import (
    create_video,
    wait_for_video,
    create_and_wait,
    _check_response,
    SIZE_MAP,
    MODEL,
)


class TestCreateVideo:
    """Tests for the create_video function."""

    @patch("api_client.requests.post")
    def test_auth_header(self, mock_post):
        """create_video() sends Authorization header 'Bearer {api_key}'."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "test123"}
        mock_post.return_value = mock_resp

        create_video("test-key", "A test prompt")

        call_headers = mock_post.call_args[1]["headers"]
        assert call_headers["Authorization"] == "Bearer test-key"

    @patch("api_client.requests.post")
    def test_model_id(self, mock_post):
        """create_video() sends payload with correct model identifier."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "test123"}
        mock_post.return_value = mock_resp

        create_video("test-key", "A test prompt")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["model"] == "doubao-seedance-2-0-260128"

    @patch("api_client.requests.post")
    def test_create_video_success(self, mock_post):
        """create_video() with valid response returns the video ID string."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "video_abc"}
        mock_post.return_value = mock_resp

        result = create_video("test-key", "A test prompt")

        assert result == "video_abc"

    @patch("api_client.requests.post")
    def test_create_video_no_id(self, mock_post):
        """create_video() raises RuntimeError when response has no id or video_id field."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_resp

        import pytest
        with pytest.raises(RuntimeError, match="No video ID"):
            create_video("test-key", "A test prompt")

    @patch("api_client.requests.post")
    def test_create_video_size_1080p(self, mock_post):
        """create_video() with resolution='1080p' does NOT include 'size' in payload."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "test123"}
        mock_post.return_value = mock_resp

        create_video("test-key", "A test prompt", resolution="1080p")

        call_json = mock_post.call_args[1]["json"]
        assert "size" not in call_json

    @patch("api_client.requests.post")
    def test_create_video_size_720p(self, mock_post):
        """create_video() with resolution='720p' ratio='16:9' includes size='1280x720'."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "test123"}
        mock_post.return_value = mock_resp

        create_video("test-key", "A test prompt", resolution="720p", ratio="16:9")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["size"] == "1280x720"


class TestWaitForVideo:
    """Tests for the wait_for_video function."""

    @patch("api_client.time.sleep")
    @patch("api_client.requests.get")
    def test_polling_completed(self, mock_get, mock_sleep):
        """wait_for_video() returns result dict after queued -> in_progress -> completed."""
        responses = [
            MagicMock(
                status_code=200,
                json=MagicMock(return_value={
                    "status": "queued",
                    "progress": 0,
                }),
            ),
            MagicMock(
                status_code=200,
                json=MagicMock(return_value={
                    "status": "in_progress",
                    "progress": 50,
                }),
            ),
            MagicMock(
                status_code=200,
                json=MagicMock(return_value={
                    "status": "completed",
                    "progress": 100,
                    "video_url": "https://example.com/v.mp4",
                }),
            ),
        ]
        mock_get.side_effect = responses

        result = wait_for_video("test-key", "video_abc", poll_interval=1, max_wait=30)

        assert result["video_url"] == "https://example.com/v.mp4"
        assert result["status"] == "completed"

    @patch("api_client.time.sleep")
    @patch("api_client.requests.get")
    def test_polling_failed(self, mock_get, mock_sleep):
        """wait_for_video() raises RuntimeError when status becomes 'failed'."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": "failed",
            "error": {"message": "Content violation"},
        }
        mock_get.return_value = mock_resp

        import pytest
        with pytest.raises(RuntimeError, match="Content violation"):
            wait_for_video("test-key", "video_abc", poll_interval=1, max_wait=30)

    @patch("api_client.time.sleep")
    @patch("api_client.requests.get")
    def test_polling_timeout(self, mock_get, mock_sleep):
        """wait_for_video() raises RuntimeError when max_wait is exceeded."""
        # Always return in_progress so it never completes
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": "in_progress",
            "progress": 50,
        }
        mock_get.return_value = mock_resp

        import pytest
        with pytest.raises(RuntimeError, match="timed out"):
            # max_wait=1, poll_interval=2 so first poll uses 2s which exceeds max_wait
            wait_for_video("test-key", "video_abc", poll_interval=2, max_wait=1)

    @patch("api_client.time.sleep")
    @patch("api_client.requests.get")
    def test_polling_network_error(self, mock_get, mock_sleep):
        """wait_for_video() catches RequestException, logs, and retries."""
        # First call raises network error, second returns completed
        error_resp = requests.RequestException("Connection error")
        success_resp = MagicMock(
            status_code=200,
            json=MagicMock(return_value={
                "status": "completed",
                "progress": 100,
                "video_url": "https://example.com/v.mp4",
            }),
        )
        mock_get.side_effect = [error_resp, success_resp]

        # Should NOT raise -- it catches the error and retries
        result = wait_for_video("test-key", "video_abc", poll_interval=1, max_wait=30)

        assert result["status"] == "completed"


class TestCheckResponse:
    """Tests for the _check_response error handling function."""

    def test_error_401(self):
        """_check_response with 401 status raises RuntimeError containing Chinese auth message."""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"

        import pytest
        with pytest.raises(RuntimeError, match="认证失败"):
            _check_response(mock_resp)

    def test_error_402(self):
        """_check_response with 402 status raises RuntimeError containing Chinese balance message."""
        mock_resp = MagicMock()
        mock_resp.status_code = 402
        mock_resp.text = "Payment Required"

        import pytest
        with pytest.raises(RuntimeError, match="余额不足"):
            _check_response(mock_resp)

    def test_error_429(self):
        """_check_response with 429 status raises RuntimeError containing Chinese rate limit message."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "Too Many Requests"

        import pytest
        with pytest.raises(RuntimeError, match="请求过于频繁"):
            _check_response(mock_resp)


class TestCreateAndWait:
    """Tests for the create_and_wait orchestration function."""

    @patch("api_client.wait_for_video")
    @patch("api_client.create_video")
    def test_create_and_wait(self, mock_create, mock_wait):
        """create_and_wait() orchestrates create_video + wait_for_video."""
        mock_create.return_value = "video_xyz"
        mock_wait.return_value = {
            "status": "completed",
            "video_url": "https://example.com/result.mp4",
        }

        result = create_and_wait("test-key", "A test prompt", duration=5)

        assert result["video_url"] == "https://example.com/result.mp4"
        assert result["video_id"] == "video_xyz"
        mock_create.assert_called_once_with("test-key", "A test prompt", 5, "1080p", "16:9")
        mock_wait.assert_called_once_with("test-key", "video_xyz")

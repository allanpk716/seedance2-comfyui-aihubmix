"""Unit tests for api_client module with mocked HTTP responses."""
from unittest.mock import patch, MagicMock

import requests

from api_client import (
    create_video,
    create_i2v_video,
    create_extend_video,
    create_omni_video,
    wait_for_video,
    create_and_wait,
    create_and_wait_i2v,
    create_and_wait_extend,
    create_and_wait_omni,
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


class TestCreateI2VVideo:
    """Tests for the create_i2v_video function."""

    @patch("api_client.requests.post")
    def test_i2v_payload_has_input(self, mock_post):
        """create_i2v_video() sends payload with 'input' field containing image data URI."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_i2v_123"}
        mock_post.return_value = mock_resp

        create_i2v_video("key", "prompt", "data:image/jpeg;base64,abc")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["input"] == "data:image/jpeg;base64,abc"

    @patch("api_client.requests.post")
    def test_i2v_model_id(self, mock_post):
        """create_i2v_video() sends payload with correct model identifier."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_i2v_123"}
        mock_post.return_value = mock_resp

        create_i2v_video("key", "prompt", "data:image/jpeg;base64,abc")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["model"] == "doubao-seedance-2-0-260128"

    @patch("api_client.requests.post")
    def test_i2v_returns_video_id(self, mock_post):
        """create_i2v_video() returns video_id string from response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_i2v_123"}
        mock_post.return_value = mock_resp

        result = create_i2v_video("key", "prompt", "data:image/jpeg;base64,abc")

        assert result == "vid_i2v_123"

    @patch("api_client.requests.post")
    def test_i2v_size_720p(self, mock_post):
        """create_i2v_video() with resolution='720p' ratio='16:9' includes size='1280x720'."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_i2v_123"}
        mock_post.return_value = mock_resp

        create_i2v_video("key", "prompt", "data:image/jpeg;base64,abc", resolution="720p", ratio="16:9")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["size"] == "1280x720"

    @patch("api_client.requests.post")
    def test_i2v_size_1080p_omitted(self, mock_post):
        """create_i2v_video() with resolution='1080p' does NOT include 'size' in payload."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_i2v_123"}
        mock_post.return_value = mock_resp

        create_i2v_video("key", "prompt", "data:image/jpeg;base64,abc", resolution="1080p")

        call_json = mock_post.call_args[1]["json"]
        assert "size" not in call_json


class TestCreateAndWaitI2V:
    """Tests for the create_and_wait_i2v orchestration function."""

    @patch("api_client.wait_for_video")
    @patch("api_client.create_i2v_video")
    def test_orchestrates_correctly(self, mock_create_i2v, mock_wait):
        """create_and_wait_i2v() orchestrates create_i2v_video + wait_for_video correctly."""
        mock_create_i2v.return_value = "vid_1"
        mock_wait.return_value = {
            "status": "completed",
            "video_url": "https://example.com/i2v.mp4",
        }

        result = create_and_wait_i2v("key", "prompt", "data:image/jpeg;base64,abc")

        assert result == {"video_url": "https://example.com/i2v.mp4", "video_id": "vid_1"}

    @patch("api_client.wait_for_video")
    @patch("api_client.create_i2v_video")
    def test_passes_all_params(self, mock_create_i2v, mock_wait):
        """create_and_wait_i2v() passes all params to create_i2v_video."""
        mock_create_i2v.return_value = "vid_2"
        mock_wait.return_value = {
            "status": "completed",
            "video_url": "https://example.com/i2v2.mp4",
        }

        create_and_wait_i2v("key", "prompt", "data:image/...", duration=10, resolution="720p", ratio="9:16")

        mock_create_i2v.assert_called_once_with("key", "prompt", "data:image/...", 10, "720p", "9:16")


class TestCreateExtendVideo:
    """Tests for the create_extend_video function."""

    @patch("api_client.requests.post")
    def test_extend_payload_has_request_id(self, mock_post):
        """create_extend_video() sends payload with 'request_id' field containing the source video_id."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_ext_test"}
        mock_post.return_value = mock_resp

        create_extend_video("key", "vid_orig", "continue the scene")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["request_id"] == "vid_orig"

    @patch("api_client.requests.post")
    def test_extend_model_id(self, mock_post):
        """create_extend_video() sends payload with correct model identifier."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_ext_test"}
        mock_post.return_value = mock_resp

        create_extend_video("key", "vid_orig", "continue the scene")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["model"] == "doubao-seedance-2-0-260128"

    @patch("api_client.requests.post")
    def test_extend_returns_video_id(self, mock_post):
        """create_extend_video() returns video_id string from response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_ext_test"}
        mock_post.return_value = mock_resp

        result = create_extend_video("key", "vid_orig", "continue the scene")

        assert result == "vid_ext_test"

    @patch("api_client.requests.post")
    def test_extend_size_720p(self, mock_post):
        """create_extend_video() with resolution='720p' ratio='16:9' includes size='1280x720'."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_ext_test"}
        mock_post.return_value = mock_resp

        create_extend_video("key", "vid_orig", "prompt", resolution="720p", ratio="16:9")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["size"] == "1280x720"

    @patch("api_client.requests.post")
    def test_extend_size_1080p_omitted(self, mock_post):
        """create_extend_video() with resolution='1080p' does NOT include 'size' in payload."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_ext_test"}
        mock_post.return_value = mock_resp

        create_extend_video("key", "vid_orig", "prompt", resolution="1080p")

        call_json = mock_post.call_args[1]["json"]
        assert "size" not in call_json

    @patch("api_client.requests.post")
    def test_extend_empty_prompt(self, mock_post):
        """create_extend_video() works when prompt is empty string."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_ext_test"}
        mock_post.return_value = mock_resp

        result = create_extend_video("key", "vid_orig", "")

        assert result == "vid_ext_test"
        call_json = mock_post.call_args[1]["json"]
        assert call_json["prompt"] == ""


class TestCreateAndWaitExtend:
    """Tests for the create_and_wait_extend orchestration function."""

    @patch("api_client.wait_for_video")
    @patch("api_client.create_extend_video")
    def test_orchestrates_correctly(self, mock_create_extend, mock_wait):
        """create_and_wait_extend() orchestrates create_extend_video + wait_for_video correctly."""
        mock_create_extend.return_value = "vid_ext_1"
        mock_wait.return_value = {
            "status": "completed",
            "video_url": "https://example.com/extend.mp4",
        }

        result = create_and_wait_extend("key", "vid_orig", "continue")

        assert result == {"video_url": "https://example.com/extend.mp4", "video_id": "vid_ext_1"}

    @patch("api_client.wait_for_video")
    @patch("api_client.create_extend_video")
    def test_passes_all_params(self, mock_create_extend, mock_wait):
        """create_and_wait_extend() passes all params to create_extend_video."""
        mock_create_extend.return_value = "vid_ext_2"
        mock_wait.return_value = {
            "status": "completed",
            "video_url": "https://example.com/extend2.mp4",
        }

        create_and_wait_extend("key", "vid_orig", "more", duration=10, resolution="720p", ratio="9:16")

        mock_create_extend.assert_called_once_with("key", "vid_orig", "more", 10, "720p", "9:16")


class TestCreateOmniVideo:
    """Tests for the create_omni_video function."""

    @patch("api_client.requests.post")
    def test_omni_payload_with_images(self, mock_post):
        """create_omni_video() sends payload with 'input' field containing list of data URIs."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_omni_test"}
        mock_post.return_value = mock_resp

        create_omni_video("key", "test prompt", image_data_uris=["data:image/jpeg;base64,abc", "data:image/jpeg;base64,def"])

        call_json = mock_post.call_args[1]["json"]
        assert call_json["input"] == ["data:image/jpeg;base64,abc", "data:image/jpeg;base64,def"]

    @patch("api_client.requests.post")
    def test_omni_payload_with_videos(self, mock_post):
        """create_omni_video() sends payload with 'video_urls' field containing list of URLs."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_omni_test"}
        mock_post.return_value = mock_resp

        create_omni_video("key", "test prompt", video_urls=["https://example.com/v1.mp4"])

        call_json = mock_post.call_args[1]["json"]
        assert call_json["video_urls"] == ["https://example.com/v1.mp4"]

    @patch("api_client.requests.post")
    def test_omni_payload_no_images_no_videos(self, mock_post):
        """create_omni_video() with no images/videos does NOT include 'input' or 'video_urls' keys."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_omni_test"}
        mock_post.return_value = mock_resp

        create_omni_video("key", "test prompt")

        call_json = mock_post.call_args[1]["json"]
        assert "input" not in call_json
        assert "video_urls" not in call_json

    @patch("api_client.requests.post")
    def test_omni_model_id(self, mock_post):
        """create_omni_video() sends payload with correct model identifier."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_omni_test"}
        mock_post.return_value = mock_resp

        create_omni_video("key", "test prompt")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["model"] == "doubao-seedance-2-0-260128"

    @patch("api_client.requests.post")
    def test_omni_returns_video_id(self, mock_post):
        """create_omni_video() returns video_id string from response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_omni_test"}
        mock_post.return_value = mock_resp

        result = create_omni_video("key", "test prompt")

        assert result == "vid_omni_test"

    @patch("api_client.requests.post")
    def test_omni_size_720p(self, mock_post):
        """create_omni_video() with resolution='720p' ratio='16:9' includes size='1280x720'."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_omni_test"}
        mock_post.return_value = mock_resp

        create_omni_video("key", "prompt", resolution="720p", ratio="16:9")

        call_json = mock_post.call_args[1]["json"]
        assert call_json["size"] == "1280x720"

    @patch("api_client.requests.post")
    def test_omni_size_1080p_omitted(self, mock_post):
        """create_omni_video() with resolution='1080p' does NOT include 'size' in payload."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "vid_omni_test"}
        mock_post.return_value = mock_resp

        create_omni_video("key", "prompt", resolution="1080p")

        call_json = mock_post.call_args[1]["json"]
        assert "size" not in call_json


class TestCreateAndWaitOmni:
    """Tests for the create_and_wait_omni orchestration function."""

    @patch("api_client.wait_for_video")
    @patch("api_client.create_omni_video")
    def test_orchestrates_correctly(self, mock_create_omni, mock_wait):
        """create_and_wait_omni() orchestrates create_omni_video + wait_for_video correctly."""
        mock_create_omni.return_value = "vid_omni_1"
        mock_wait.return_value = {
            "status": "completed",
            "video_url": "https://example.com/omni.mp4",
        }

        result = create_and_wait_omni("key", "prompt")

        assert result == {"video_url": "https://example.com/omni.mp4", "video_id": "vid_omni_1"}

    @patch("api_client.wait_for_video")
    @patch("api_client.create_omni_video")
    def test_passes_all_params(self, mock_create_omni, mock_wait):
        """create_and_wait_omni() passes all params to create_omni_video."""
        mock_create_omni.return_value = "vid_omni_2"
        mock_wait.return_value = {
            "status": "completed",
            "video_url": "https://example.com/omni2.mp4",
        }

        create_and_wait_omni(
            "key", "prompt",
            image_data_uris=["data:image/jpeg;base64,abc"],
            video_urls=["https://example.com/v1.mp4"],
            duration=10, resolution="720p", ratio="9:16",
        )

        mock_create_omni.assert_called_once_with(
            "key", "prompt",
            ["data:image/jpeg;base64,abc"],
            ["https://example.com/v1.mp4"],
            10, "720p", "9:16",
        )

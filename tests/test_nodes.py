"""Unit tests for SeedanceApiKey and SeedanceTextToVideo node classes."""
import os
import io

import cv2
import numpy as np
import torch
from unittest.mock import MagicMock, patch, mock_open

import pytest


class TestSeedanceApiKey:
    """Tests for the SeedanceApiKey node class."""

    def test_api_key_passthrough(self):
        """SeedanceApiKey().pass_key('my-key-123') returns ('my-key-123',)."""
        from seedance_comfyui.nodes import SeedanceApiKey

        node = SeedanceApiKey()
        result = node.pass_key("my-key-123")
        assert result == ("my-key-123",)

    def test_api_key_input_types(self):
        """SeedanceApiKey.INPUT_TYPES() returns dict with required.api_key as STRING."""
        from seedance_comfyui.nodes import SeedanceApiKey

        result = SeedanceApiKey.INPUT_TYPES()
        assert "required" in result
        assert "api_key" in result["required"]
        assert result["required"]["api_key"][0] == "STRING"

    def test_api_key_return_types(self):
        """SeedanceApiKey.RETURN_TYPES == ('STRING',)."""
        from seedance_comfyui.nodes import SeedanceApiKey

        assert SeedanceApiKey.RETURN_TYPES == ("STRING",)

    def test_api_key_return_names(self):
        """SeedanceApiKey.RETURN_NAMES == ('api_key',)."""
        from seedance_comfyui.nodes import SeedanceApiKey

        assert SeedanceApiKey.RETURN_NAMES == ("api_key",)

    def test_api_key_function(self):
        """SeedanceApiKey.FUNCTION == 'pass_key'."""
        from seedance_comfyui.nodes import SeedanceApiKey

        assert SeedanceApiKey.FUNCTION == "pass_key"

    def test_api_key_category(self):
        """SeedanceApiKey.CATEGORY == 'Seedance 2.0'."""
        from seedance_comfyui.nodes import SeedanceApiKey

        assert SeedanceApiKey.CATEGORY == "Seedance 2.0"


class TestSeedanceTextToVideo:
    """Tests for the SeedanceTextToVideo node class."""

    def test_t2v_optional_key(self):
        """SeedanceTextToVideo.INPUT_TYPES()['optional'] contains 'api_key' as STRING."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        result = SeedanceTextToVideo.INPUT_TYPES()
        assert "optional" in result
        assert "api_key" in result["optional"]
        assert result["optional"]["api_key"][0] == "STRING"

    def test_t2v_prompt_required(self):
        """SeedanceTextToVideo.INPUT_TYPES()['required'] contains 'prompt' as STRING with multiline=True."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        result = SeedanceTextToVideo.INPUT_TYPES()
        assert "required" in result
        assert "prompt" in result["required"]
        assert result["required"]["prompt"][0] == "STRING"
        config = result["required"]["prompt"][1]
        assert config.get("multiline") is True

    def test_t2v_duration(self):
        """Duration config is INT with default=5, min=4, max=15."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        result = SeedanceTextToVideo.INPUT_TYPES()
        duration = result["optional"]["duration"]
        assert duration[0] == "INT"
        assert duration[1]["default"] == 5
        assert duration[1]["min"] == 4
        assert duration[1]["max"] == 15

    def test_t2v_resolution_options(self):
        """Resolution options include '1080p', '720p', '480p'."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        result = SeedanceTextToVideo.INPUT_TYPES()
        resolution = result["optional"]["resolution"]
        # ComfyUI enum format: (["a", "b", "c"],) or similar
        options = resolution[0] if isinstance(resolution[0], (list, tuple)) else resolution
        assert "1080p" in options
        assert "720p" in options
        assert "480p" in options

    def test_t2v_ratio_options(self):
        """Ratio options include all 6 values."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        result = SeedanceTextToVideo.INPUT_TYPES()
        ratio = result["optional"]["ratio"]
        options = ratio[0] if isinstance(ratio[0], (list, tuple)) else ratio
        expected = ["16:9", "9:16", "4:3", "3:4", "1:1", "21:9"]
        for r in expected:
            assert r in options

    def test_t2v_output_types(self):
        """SeedanceTextToVideo.RETURN_TYPES == ('STRING', 'STRING') -- no IMAGE per D-01."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        assert SeedanceTextToVideo.RETURN_TYPES == ("STRING", "STRING")

    def test_t2v_output_names(self):
        """SeedanceTextToVideo.RETURN_NAMES == ('video_url', 'video_id')."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        assert SeedanceTextToVideo.RETURN_NAMES == ("video_url", "video_id")

    def test_t2v_function(self):
        """SeedanceTextToVideo.FUNCTION == 'generate'."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        assert SeedanceTextToVideo.FUNCTION == "generate"

    def test_t2v_category(self):
        """SeedanceTextToVideo.CATEGORY == 'Seedance 2.0'."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        assert SeedanceTextToVideo.CATEGORY == "Seedance 2.0"

    def test_missing_key_error(self):
        """Missing API key raises ValueError with guidance about aihubmix.com."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        node = SeedanceTextToVideo()
        with pytest.raises(ValueError, match="(?i)api.key|aihubmix"):
            node.generate(prompt="test", api_key="")

    @patch("seedance_comfyui.nodes.create_and_wait")
    def test_t2v_calls_create_and_wait(self, mock_create_and_wait):
        """T2V node calls create_and_wait with correct args, returns (video_url, video_id)."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        mock_create_and_wait.return_value = {
            "video_url": "https://example.com/v.mp4",
            "video_id": "vid_123",
        }

        node = SeedanceTextToVideo()
        result = node.generate(
            prompt="a cat",
            api_key="key123",
            duration=5,
            resolution="1080p",
            ratio="16:9",
        )

        mock_create_and_wait.assert_called_once_with(
            "key123", "a cat", 5, "1080p", "16:9"
        )
        assert result == ("https://example.com/v.mp4", "vid_123")

    @patch("seedance_comfyui.nodes.create_and_wait")
    def test_t2v_size_options(self, mock_create_and_wait):
        """T2V node passes resolution and ratio through to create_and_wait."""
        from seedance_comfyui.nodes import SeedanceTextToVideo

        mock_create_and_wait.return_value = {
            "video_url": "https://example.com/v2.mp4",
            "video_id": "vid_456",
        }

        node = SeedanceTextToVideo()
        result = node.generate(
            prompt="a dog",
            api_key="key456",
            duration=10,
            resolution="720p",
            ratio="9:16",
        )

        mock_create_and_wait.assert_called_once_with(
            "key456", "a dog", 10, "720p", "9:16"
        )
        assert result == ("https://example.com/v2.mp4", "vid_456")


class TestSeedanceImageToVideo:
    """Tests for the SeedanceImageToVideo node class."""

    def test_i2v_image_required(self):
        """SeedanceImageToVideo.INPUT_TYPES()['required'] contains 'image' as IMAGE type."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        result = SeedanceImageToVideo.INPUT_TYPES()
        assert "required" in result
        assert "image" in result["required"]
        assert result["required"]["image"][0] == "IMAGE"

    def test_i2v_prompt_required(self):
        """SeedanceImageToVideo.INPUT_TYPES()['required'] contains 'prompt' as multiline STRING."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        result = SeedanceImageToVideo.INPUT_TYPES()
        assert "prompt" in result["required"]
        assert result["required"]["prompt"][0] == "STRING"
        config = result["required"]["prompt"][1]
        assert config.get("multiline") is True

    def test_i2v_optional_fields(self):
        """SeedanceImageToVideo optional fields match T2V pattern."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        result = SeedanceImageToVideo.INPUT_TYPES()
        assert "optional" in result
        assert result["optional"]["api_key"][0] == "STRING"
        duration = result["optional"]["duration"]
        assert duration[0] == "INT"
        assert duration[1]["default"] == 5
        assert duration[1]["min"] == 4
        assert duration[1]["max"] == 15
        resolution = result["optional"]["resolution"]
        assert "1080p" in resolution[0]
        ratio = result["optional"]["ratio"]
        assert "16:9" in ratio[0]

    def test_i2v_output_types(self):
        """SeedanceImageToVideo.RETURN_TYPES == ('STRING', 'STRING') per D-10."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        assert SeedanceImageToVideo.RETURN_TYPES == ("STRING", "STRING")

    def test_i2v_output_names(self):
        """SeedanceImageToVideo.RETURN_NAMES == ('video_url', 'video_id') per D-10."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        assert SeedanceImageToVideo.RETURN_NAMES == ("video_url", "video_id")

    def test_i2v_function(self):
        """SeedanceImageToVideo.FUNCTION == 'generate'."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        assert SeedanceImageToVideo.FUNCTION == "generate"

    def test_i2v_category(self):
        """SeedanceImageToVideo.CATEGORY == 'Seedance 2.0'."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        assert SeedanceImageToVideo.CATEGORY == "Seedance 2.0"

    def test_i2v_output_node(self):
        """SeedanceImageToVideo.OUTPUT_NODE == False."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        assert SeedanceImageToVideo.OUTPUT_NODE is False

    def test_i2v_missing_key_error(self):
        """Missing API key raises ValueError with aihubmix guidance."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        import torch
        node = SeedanceImageToVideo()
        fake_image = torch.rand(1, 64, 64, 3)
        with pytest.raises(ValueError, match="(?i)api.key|aihubmix"):
            node.generate(image=fake_image, prompt="test", api_key="")

    @patch("seedance_comfyui.nodes.create_and_wait_i2v")
    def test_i2v_calls_create_and_wait_i2v(self, mock_create_and_wait_i2v):
        """I2V node calls create_and_wait_i2v with correct args."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        import torch
        mock_create_and_wait_i2v.return_value = {
            "video_url": "https://example.com/i2v.mp4",
            "video_id": "vid_i2v_123",
        }

        node = SeedanceImageToVideo()
        fake_image = torch.rand(1, 64, 64, 3)
        result = node.generate(
            image=fake_image,
            prompt="a cat sitting",
            api_key="key123",
            duration=5,
            resolution="1080p",
            ratio="16:9",
        )

        assert mock_create_and_wait_i2v.call_count == 1
        call_args = mock_create_and_wait_i2v.call_args
        assert call_args[0][0] == "key123"
        assert call_args[0][1] == "a cat sitting"
        assert call_args[0][2].startswith("data:image/jpeg;base64,")
        assert call_args[0][3] == 5
        assert call_args[0][4] == "1080p"
        assert call_args[0][5] == "16:9"

    @patch("seedance_comfyui.nodes.create_and_wait_i2v")
    def test_i2v_tensor_to_data_uri(self, mock_create_and_wait_i2v):
        """I2V node converts IMAGE tensor to base64 data URI starting with data:image/jpeg;base64,"""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        import torch
        mock_create_and_wait_i2v.return_value = {
            "video_url": "https://example.com/i2v.mp4",
            "video_id": "vid_i2v_456",
        }

        node = SeedanceImageToVideo()
        fake_image = torch.rand(1, 2, 2, 3)
        node.generate(image=fake_image, prompt="test", api_key="key")

        call_args = mock_create_and_wait_i2v.call_args[0]
        data_uri = call_args[2]
        assert data_uri.startswith("data:image/jpeg;base64,")
        # Verify base64 content is non-empty
        b64_part = data_uri.split(",", 1)[1]
        assert len(b64_part) > 0

    @patch("seedance_comfyui.nodes.create_and_wait_i2v")
    def test_i2v_returns_tuple(self, mock_create_and_wait_i2v):
        """I2V node returns (video_url, video_id) tuple."""
        from seedance_comfyui.nodes import SeedanceImageToVideo

        import torch
        mock_create_and_wait_i2v.return_value = {
            "video_url": "https://example.com/i2v.mp4",
            "video_id": "vid_i2v_789",
        }

        node = SeedanceImageToVideo()
        fake_image = torch.rand(1, 64, 64, 3)
        result = node.generate(image=fake_image, prompt="test", api_key="key")

        assert result == ("https://example.com/i2v.mp4", "vid_i2v_789")


class TestSeedanceSaveVideo:
    """Tests for the SeedanceSaveVideo OUTPUT_NODE class."""

    # --- Static attribute tests ---

    def test_save_video_url_required(self):
        """SeedanceSaveVideo INPUT_TYPES has video_url as required STRING."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        result = SeedanceSaveVideo.INPUT_TYPES()
        assert "required" in result
        assert "video_url" in result["required"]
        assert result["required"]["video_url"][0] == "STRING"

    def test_save_optional_fields(self):
        """SeedanceSaveVideo optional fields: filename_prefix, subfolder, frame_load_cap."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        result = SeedanceSaveVideo.INPUT_TYPES()
        assert "optional" in result

        fp = result["optional"]["filename_prefix"]
        assert fp[0] == "STRING"
        assert fp[1]["default"] == "Seedance"

        sf = result["optional"]["subfolder"]
        assert sf[0] == "STRING"
        assert sf[1]["default"] == ""

        flc = result["optional"]["frame_load_cap"]
        assert flc[0] == "INT"
        assert flc[1]["default"] == 16
        assert flc[1]["min"] == 1
        assert flc[1]["max"] == 1000

    def test_save_output_types(self):
        """SeedanceSaveVideo.RETURN_TYPES == ('IMAGE', 'STRING', 'STRING') per D-12."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        assert SeedanceSaveVideo.RETURN_TYPES == ("IMAGE", "STRING", "STRING")

    def test_save_output_names(self):
        """SeedanceSaveVideo.RETURN_NAMES == ('frames', 'first_frame_path', 'video_path') per D-12."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        assert SeedanceSaveVideo.RETURN_NAMES == ("frames", "first_frame_path", "video_path")

    def test_save_function(self):
        """SeedanceSaveVideo.FUNCTION == 'save'."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        assert SeedanceSaveVideo.FUNCTION == "save"

    def test_save_category(self):
        """SeedanceSaveVideo.CATEGORY == 'Seedance 2.0'."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        assert SeedanceSaveVideo.CATEGORY == "Seedance 2.0"

    def test_save_is_output_node(self):
        """SeedanceSaveVideo.OUTPUT_NODE == True per D-12b."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        assert SeedanceSaveVideo.OUTPUT_NODE is True

    def test_save_empty_url_error(self):
        """Empty video_url raises ValueError with Chinese error message."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        node = SeedanceSaveVideo()
        with pytest.raises(ValueError, match="视频|链接|不能为空"):
            node.save(video_url="")

    # --- Integration tests using fixtures ---

    def test_save_downloads_video(self, mock_folder_paths, mock_video_bytes, tmp_path):
        """save() downloads video from URL via requests.get(stream=True) and writes .mp4 file."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        # Mock requests.get to return our test video bytes as a streaming response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = MagicMock(return_value=[mock_video_bytes])
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("seedance_comfyui.nodes.requests.get", return_value=mock_resp) as mock_get:
            node = SeedanceSaveVideo()
            result = node.save(video_url="https://example.com/video.mp4")

            # Verify requests.get called with stream=True
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args
            assert call_kwargs[1].get("stream") is True or (len(call_kwargs) > 1 and call_kwargs[1].get("stream") is True)

            # Verify an .mp4 file was written to the output directory
            output_dir = mock_folder_paths.get_output_directory()
            mp4_files = [f for f in os.listdir(output_dir) if f.endswith(".mp4")]
            assert len(mp4_files) >= 1

    def test_save_extracts_frames(self, mock_folder_paths, mock_video_bytes, tmp_path):
        """save() extracts frames as ComfyUI IMAGE tensor (N,H,W,C float32 [0,1])."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = MagicMock(return_value=[mock_video_bytes])
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("seedance_comfyui.nodes.requests.get", return_value=mock_resp):
            node = SeedanceSaveVideo()
            result = node.save(video_url="https://example.com/video.mp4")

            frames = result["result"][0]
            assert isinstance(frames, torch.Tensor)
            assert frames.dtype == torch.float32
            assert frames.dim() == 4  # (N, H, W, C)
            assert frames.shape[0] <= 16  # frame_load_cap default
            assert frames.shape[3] == 3  # RGB channels
            assert frames.min() >= 0.0
            assert frames.max() <= 1.0

    def test_save_frame_load_cap(self, mock_folder_paths, mock_video_bytes, tmp_path):
        """save() with frame_load_cap=2 extracts exactly 2 frames."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = MagicMock(return_value=[mock_video_bytes])
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("seedance_comfyui.nodes.requests.get", return_value=mock_resp):
            node = SeedanceSaveVideo()
            result = node.save(video_url="https://example.com/video.mp4", frame_load_cap=2)

            frames = result["result"][0]
            assert frames.shape[0] == 2

    def test_save_first_frame_png(self, mock_folder_paths, mock_video_bytes, tmp_path):
        """save() saves first frame as PNG and returns matching first_frame_path."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = MagicMock(return_value=[mock_video_bytes])
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("seedance_comfyui.nodes.requests.get", return_value=mock_resp):
            node = SeedanceSaveVideo()
            result = node.save(video_url="https://example.com/video.mp4")

            first_frame_path = result["result"][1]
            assert first_frame_path.endswith(".png")
            assert os.path.exists(first_frame_path)

    def test_save_ui_preview(self, mock_folder_paths, mock_video_bytes, tmp_path):
        """save() returns dict with 'ui' key containing 'images' list per D-12c."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = MagicMock(return_value=[mock_video_bytes])
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("seedance_comfyui.nodes.requests.get", return_value=mock_resp):
            node = SeedanceSaveVideo()
            result = node.save(video_url="https://example.com/video.mp4")

            assert "ui" in result
            assert "images" in result["ui"]
            images = result["ui"]["images"]
            assert len(images) >= 1
            assert images[0]["filename"].endswith(".mp4")
            assert images[0]["type"] == "output"

    def test_save_result_tuple(self, mock_folder_paths, mock_video_bytes, tmp_path):
        """save() returns dict with 'result' key containing (frames, first_frame_path, video_path)."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = MagicMock(return_value=[mock_video_bytes])
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("seedance_comfyui.nodes.requests.get", return_value=mock_resp):
            node = SeedanceSaveVideo()
            result = node.save(video_url="https://example.com/video.mp4")

            assert "result" in result
            res = result["result"]
            assert len(res) == 3
            frames, first_frame_path, video_path = res
            assert isinstance(frames, torch.Tensor)
            assert isinstance(first_frame_path, str)
            assert isinstance(video_path, str)
            assert video_path.endswith(".mp4")

    def test_save_custom_prefix(self, mock_folder_paths, mock_video_bytes, tmp_path):
        """save() with filename_prefix='MyVideo' creates files starting with 'MyVideo_'."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = MagicMock(return_value=[mock_video_bytes])
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("seedance_comfyui.nodes.requests.get", return_value=mock_resp):
            node = SeedanceSaveVideo()
            result = node.save(video_url="https://example.com/video.mp4", filename_prefix="MyVideo")

            video_path = result["result"][2]
            basename = os.path.basename(video_path)
            assert basename.startswith("MyVideo_")

    def test_save_subfolder(self, mock_folder_paths, mock_video_bytes, tmp_path):
        """save() with subfolder='test_sub' saves video in that subdirectory."""
        from seedance_comfyui.nodes import SeedanceSaveVideo

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_content = MagicMock(return_value=[mock_video_bytes])
        mock_resp.raise_for_status = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("seedance_comfyui.nodes.requests.get", return_value=mock_resp):
            node = SeedanceSaveVideo()
            result = node.save(video_url="https://example.com/video.mp4", subfolder="test_sub")

            video_path = result["result"][2]
            assert "test_sub" in video_path
            assert os.path.exists(video_path)


class TestSeedanceExtendVideo:
    """Tests for the SeedanceExtendVideo node class."""

    def test_extend_video_id_required(self):
        """SeedanceExtendVideo.INPUT_TYPES()['required'] contains 'video_id' as STRING type."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        result = SeedanceExtendVideo.INPUT_TYPES()
        assert "required" in result
        assert "video_id" in result["required"]
        assert result["required"]["video_id"][0] == "STRING"

    def test_extend_prompt_required(self):
        """SeedanceExtendVideo.INPUT_TYPES()['required'] contains 'prompt' as multiline STRING."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        result = SeedanceExtendVideo.INPUT_TYPES()
        assert "prompt" in result["required"]
        assert result["required"]["prompt"][0] == "STRING"
        config = result["required"]["prompt"][1]
        assert config.get("multiline") is True

    def test_extend_optional_fields(self):
        """SeedanceExtendVideo optional fields match T2V/I2V pattern."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        result = SeedanceExtendVideo.INPUT_TYPES()
        assert "optional" in result
        assert result["optional"]["api_key"][0] == "STRING"
        duration = result["optional"]["duration"]
        assert duration[0] == "INT"
        assert duration[1]["default"] == 5
        assert duration[1]["min"] == 4
        assert duration[1]["max"] == 15
        resolution = result["optional"]["resolution"]
        assert "1080p" in resolution[0]
        assert "720p" in resolution[0]
        assert "480p" in resolution[0]
        ratio = result["optional"]["ratio"]
        expected_ratios = ["16:9", "9:16", "4:3", "3:4", "1:1", "21:9"]
        for r in expected_ratios:
            assert r in ratio[0]

    def test_extend_output_types(self):
        """SeedanceExtendVideo.RETURN_TYPES == ('STRING', 'STRING') per D-15."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        assert SeedanceExtendVideo.RETURN_TYPES == ("STRING", "STRING")

    def test_extend_output_names(self):
        """SeedanceExtendVideo.RETURN_NAMES == ('video_url', 'video_id') per D-15."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        assert SeedanceExtendVideo.RETURN_NAMES == ("video_url", "video_id")

    def test_extend_function(self):
        """SeedanceExtendVideo.FUNCTION == 'generate'."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        assert SeedanceExtendVideo.FUNCTION == "generate"

    def test_extend_category(self):
        """SeedanceExtendVideo.CATEGORY == 'Seedance 2.0'."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        assert SeedanceExtendVideo.CATEGORY == "Seedance 2.0"

    def test_extend_output_node(self):
        """SeedanceExtendVideo.OUTPUT_NODE == False."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        assert SeedanceExtendVideo.OUTPUT_NODE is False

    def test_extend_missing_key_error(self):
        """Missing API key raises ValueError with aihubmix guidance."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        node = SeedanceExtendVideo()
        with pytest.raises(ValueError, match="(?i)api.key|aihubmix"):
            node.generate(video_id="vid_123", prompt="test", api_key="")

    def test_extend_missing_video_id_error(self):
        """Empty video_id raises ValueError with Chinese error message."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        node = SeedanceExtendVideo()
        with pytest.raises(ValueError, match="视频|ID|不能为空"):
            node.generate(video_id="", prompt="test", api_key="key123")

    @patch("seedance_comfyui.nodes.create_and_wait_extend")
    def test_extend_calls_create_and_wait_extend(self, mock_create_and_wait_extend):
        """Extend node calls create_and_wait_extend with correct args, returns (video_url, video_id)."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        mock_create_and_wait_extend.return_value = {
            "video_url": "https://example.com/extend.mp4",
            "video_id": "vid_ext_123",
        }

        node = SeedanceExtendVideo()
        result = node.generate(
            video_id="vid_123",
            prompt="continue",
            api_key="key123",
        )

        mock_create_and_wait_extend.assert_called_once_with(
            "key123", "vid_123", "continue", 5, "1080p", "16:9"
        )
        assert result == ("https://example.com/extend.mp4", "vid_ext_123")

    @patch("seedance_comfyui.nodes.create_and_wait_extend")
    def test_extend_size_options(self, mock_create_and_wait_extend):
        """Extend node passes resolution and ratio through to create_and_wait_extend."""
        from seedance_comfyui.nodes import SeedanceExtendVideo

        mock_create_and_wait_extend.return_value = {
            "video_url": "https://example.com/extend2.mp4",
            "video_id": "vid_ext_456",
        }

        node = SeedanceExtendVideo()
        result = node.generate(
            video_id="vid_456",
            prompt="more action",
            api_key="key456",
            duration=10,
            resolution="720p",
            ratio="9:16",
        )

        mock_create_and_wait_extend.assert_called_once_with(
            "key456", "vid_456", "more action", 10, "720p", "9:16"
        )
        assert result == ("https://example.com/extend2.mp4", "vid_ext_456")

"""Unit tests for SeedanceApiKey and SeedanceTextToVideo node classes."""
from unittest.mock import patch

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

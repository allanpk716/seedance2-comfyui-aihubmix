"""ComfyUI node classes for Seedance 2.0 video generation.

Provides two node classes:
- SeedanceApiKey: Passthrough node for wiring API keys to generation nodes.
- SeedanceTextToVideo: Text-to-video generation via AIHubMix API.
"""
from .api_client import create_and_wait


class SeedanceApiKey:
    """Dedicated node for entering and wiring the AIHubMix API key.

    Users connect this node's output to generation nodes (Text-to-Video, etc.)
    so the API key is entered once and shared across the workflow.
    """

    CATEGORY = "Seedance 2.0"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("api_key",)
    FUNCTION = "pass_key"
    OUTPUT_NODE = False

    def pass_key(self, api_key):
        return (api_key,)


class SeedanceTextToVideo:
    """Text-to-video generation node using Seedance 2.0 via AIHubMix.

    Accepts a text prompt and optional parameters (duration, resolution, ratio).
    The api_key can be provided via wiring from a SeedanceApiKey node or
    filled in directly as an optional field.
    """

    CATEGORY = "Seedance 2.0"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "duration": ("INT", {"default": 5, "min": 4, "max": 15, "step": 1}),
                "resolution": (["1080p", "720p", "480p"],),
                "ratio": (["16:9", "9:16", "4:3", "3:4", "1:1", "21:9"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "video_id")
    FUNCTION = "generate"
    OUTPUT_NODE = False

    def generate(self, prompt, api_key="", duration=5, resolution="1080p", ratio="16:9"):
        if not api_key:
            raise ValueError(
                "API key is required. "
                "Please connect a Seedance 2.0 API Key node or fill in the api_key field. "
                "You can get your key at aihubmix.com"
            )
        result = create_and_wait(api_key, prompt, duration, resolution, ratio)
        return (result["video_url"], result["video_id"])

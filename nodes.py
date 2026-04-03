"""ComfyUI node classes for Seedance 2.0 video generation.

Provides node classes:
- SeedanceApiKey: Passthrough node for wiring API keys to generation nodes.
- SeedanceTextToVideo: Text-to-video generation via AIHubMix API.
- SeedanceImageToVideo: Image-to-video generation with reference image input.
"""
import base64
import io

import numpy as np
from PIL import Image

from .api_client import create_and_wait
from .api_client import create_and_wait_i2v


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


class SeedanceImageToVideo:
    """Image-to-video generation node using Seedance 2.0 via AIHubMix.

    Accepts a ComfyUI IMAGE tensor (reference image) and a text prompt.
    The image tensor is converted to a JPEG base64 data URI per D-13
    and sent as the "input" field in the API payload.
    """

    CATEGORY = "Seedance 2.0"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
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

    def generate(self, image, prompt, api_key="", duration=5, resolution="1080p", ratio="16:9"):
        if not api_key:
            raise ValueError(
                "API key is required. "
                "Please connect a Seedance 2.0 API Key node or fill in the api_key field. "
                "You can get your key at aihubmix.com"
            )
        # Convert IMAGE tensor to base64 JPEG data URI per D-13
        image_array = np.clip(image[0].cpu().numpy() * 255, 0, 255).astype(np.uint8)
        pil_image = Image.fromarray(image_array)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=95)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{encoded}"

        result = create_and_wait_i2v(api_key, prompt, data_uri, duration, resolution, ratio)
        return (result["video_url"], result["video_id"])

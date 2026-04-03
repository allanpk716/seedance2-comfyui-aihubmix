"""ComfyUI node classes for Seedance 2.0 video generation.

Provides node classes:
- SeedanceApiKey: Passthrough node for wiring API keys to generation nodes.
- SeedanceTextToVideo: Text-to-video generation via AIHubMix API.
- SeedanceImageToVideo: Image-to-video generation with reference image input.
- SeedanceSaveVideo: OUTPUT_NODE that downloads video, extracts frames, and previews.
"""
import base64
import io
import os
import uuid

import cv2
import numpy as np
import requests
import torch
from PIL import Image

from .api_client import create_and_wait
from .api_client import create_and_wait_i2v
from .api_client import create_and_wait_extend
from .api_client import create_and_wait_omni


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


class SeedanceExtendVideo:
    """Video extend node using Seedance 2.0 via AIHubMix.

    Accepts a video_id from a prior generation and an optional continuation prompt.
    The video_id is sent as request_id in the payload to extend the original video.
    """

    CATEGORY = "Seedance 2.0"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_id": ("STRING", {"default": ""}),
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

    def generate(self, video_id, prompt="", api_key="", duration=5, resolution="1080p", ratio="16:9"):
        if not api_key:
            raise ValueError(
                "API key is required. "
                "Please connect a Seedance 2.0 API Key node or fill in the api_key field. "
                "You can get your key at aihubmix.com"
            )
        if not video_id:
            raise ValueError("视频ID不能为空。请将视频生成节点的 video_id 输出连接到此节点。")
        result = create_and_wait_extend(api_key, video_id, prompt, duration, resolution, ratio)
        return (result["video_url"], result["video_id"])


class SeedanceOmniReference:
    """Omni reference video generation node using Seedance 2.0 via AIHubMix.

    Combines up to 9 reference images and up to 3 video URLs with a text prompt
    for multi-modal video generation per OMNI-01/OMNI-02/OMNI-03.
    Unconnected image/video slots are silently ignored.
    """

    CATEGORY = "Seedance 2.0"

    @classmethod
    def INPUT_TYPES(cls):
        optional = {
            "api_key": ("STRING", {"default": ""}),
            "duration": ("INT", {"default": 5, "min": 4, "max": 15, "step": 1}),
            "resolution": (["1080p", "720p", "480p"],),
            "ratio": (["16:9", "9:16", "4:3", "3:4", "1:1", "21:9"],),
        }
        for i in range(1, 10):
            optional[f"image_{i}"] = ("IMAGE",)
        for i in range(1, 4):
            optional[f"video_url_{i}"] = ("STRING", {"default": ""})
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": optional,
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "video_id")
    FUNCTION = "generate"
    OUTPUT_NODE = False

    def generate(self, prompt, api_key="", duration=5, resolution="1080p", ratio="16:9", **kwargs):
        if not api_key:
            raise ValueError(
                "API key is required. "
                "Please connect a Seedance 2.0 API Key node or fill in the api_key field. "
                "You can get your key at aihubmix.com"
            )

        # Convert connected images to base64 JPEG data URIs per D-13
        image_data_uris = []
        for i in range(1, 10):
            img = kwargs.get(f"image_{i}")
            if img is not None:
                image_array = np.clip(img[0].cpu().numpy() * 255, 0, 255).astype(np.uint8)
                pil_image = Image.fromarray(image_array)
                buffer = io.BytesIO()
                pil_image.save(buffer, format="JPEG", quality=95)
                encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
                image_data_uris.append(f"data:image/jpeg;base64,{encoded}")

        # Collect connected video URLs (skip empty strings)
        video_urls = []
        for i in range(1, 4):
            url = kwargs.get(f"video_url_{i}", "")
            if url:
                video_urls.append(url)

        result = create_and_wait_omni(
            api_key, prompt,
            image_data_uris or None,
            video_urls or None,
            duration, resolution, ratio,
        )
        return (result["video_url"], result["video_id"])


class SeedanceSaveVideo:
    """OUTPUT_NODE that downloads a generated video, extracts frames as ComfyUI IMAGE tensors,
    saves the first frame as PNG, and returns a UI preview dict for the ComfyUI canvas.

    Per D-12: RETURN_TYPES = (IMAGE, STRING, STRING), OUTPUT_NODE = True.
    Per D-12a: frame_load_cap defaults to 16 to prevent OOM.
    Per D-12c: Returns dict with "ui" key for canvas preview.
    """

    CATEGORY = "Seedance 2.0"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {"default": ""}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "filename_prefix": ("STRING", {"default": "Seedance"}),
                "subfolder": ("STRING", {"default": ""}),
                "frame_load_cap": ("INT", {"default": 16, "min": 1, "max": 1000}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("frames", "first_frame_path", "video_path")
    FUNCTION = "save"

    def save(self, video_url, api_key="", filename_prefix="Seedance", subfolder="", frame_load_cap=16):
        # Validate video_url per D-08 Chinese error convention
        if not video_url:
            raise ValueError("视频链接不能为空。请将视频生成节点连接到此节点。")

        # Resolve output directory (import here to allow mocking in tests)
        import folder_paths
        output_dir = folder_paths.get_output_directory()
        target_dir = os.path.join(output_dir, subfolder) if subfolder else output_dir
        os.makedirs(target_dir, exist_ok=True)

        # Generate unique filename
        unique_id = uuid.uuid4().hex[:8]
        video_filename = f"{filename_prefix}_{unique_id}.mp4"
        video_path = os.path.join(target_dir, video_filename)

        # Download video via streaming with auth if api_key provided
        print(f"[Seedance] Downloading video to {video_path}...")
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        resp = requests.get(video_url, headers=headers, stream=True, timeout=300)
        resp.raise_for_status()
        with open(video_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract frames via cv2.VideoCapture
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"无法打开视频文件: {video_path}")

        frames = []
        while len(frames) < frame_load_cap:
            ret, frame = cap.read()
            if not ret:
                break
            # Convert BGR to RGB and normalize to float32 [0, 1]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_float = frame_rgb.astype(np.float32) / 255.0
            frames.append(frame_float)
        cap.release()

        if not frames:
            raise RuntimeError("未能从视频中提取任何帧")

        # Build frames tensor (N, H, W, C) float32 [0, 1]
        frames_tensor = torch.from_numpy(np.stack(frames, axis=0))

        # Save first frame as PNG
        first_frame_uint8 = (frames[0] * 255).astype(np.uint8)
        first_frame_filename = f"{filename_prefix}_{unique_id}_first_frame.png"
        first_frame_path = os.path.join(target_dir, first_frame_filename)
        Image.fromarray(first_frame_uint8).save(first_frame_path)

        # Build return dict per ComfyUI OUTPUT_NODE format
        return {
            "ui": {"images": [{"filename": video_filename, "subfolder": subfolder, "type": "output"}]},
            "result": (frames_tensor, first_frame_path, video_path),
        }

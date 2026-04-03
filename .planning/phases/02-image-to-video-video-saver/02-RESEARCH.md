# Phase 2: Image-to-Video + Video Saver - Research

**Researched:** 2026-04-03
**Domain:** ComfyUI custom nodes, AIHubMix Video API (I2V), video download/frame extraction
**Confidence:** HIGH

## Summary

Phase 2 adds two new capabilities to the Seedance 2.0 ComfyUI plugin: an Image-to-Video (I2V) node that accepts a ComfyUI IMAGE tensor plus a prompt to generate video with a reference image, and a Save Video node that downloads the generated video, extracts frames as ComfyUI IMAGE tensors, and enables preview in the ComfyUI UI canvas. Both nodes follow the exact same patterns established in Phase 1 -- same CATEGORY, same function-based API client extension, same mock/patch testing strategy.

The I2V node extends the existing `api_client.py` with a new `create_i2v_video` / `create_and_wait_i2v` function pair that adds the `input` field (base64 data URI) to the API payload. The image conversion pipeline is straightforward: ComfyUI IMAGE tensor (B,H,W,C float32 [0,1]) -> numpy uint8 -> PIL Image -> JPEG bytes -> base64 data URI. The Save Video node is an OUTPUT_NODE that uses ComfyUI's `folder_paths` API for output directory management, `requests` streaming for video download, and `cv2.VideoCapture` for frame extraction. The UI preview mechanism returns a dict with `{"ui": {"images": [...]}}` containing filename/subfolder/type entries.

**Primary recommendation:** Extend `api_client.py` with new I2V functions (do NOT modify existing T2V functions). Implement Save Video as an OUTPUT_NODE using ComfyUI's `folder_paths.get_output_directory()` + `get_save_image_path()` pattern from the official `SaveImage` node. Use opencv for frame extraction with a `frame_load_cap` default of 16 to prevent OOM.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-10:** I2V node outputs `(video_url: STRING, video_id: STRING)` -- same format as T2V. No IMAGE output from I2V.
- **D-11:** first_frame extraction is handled by the Save Video node (Phase 2), not by I2V.
- **D-12:** Save Video outputs `(IMAGE, STRING, STRING)` = `(frames, first_frame_path, video_path)`.
  - `frames`: All extracted video frames as ComfyUI IMAGE tensor (limited by frame_load_cap).
  - `first_frame_path`: File path to the saved first frame image.
  - `video_path`: File path to the downloaded video file.
- **D-12a:** `frame_load_cap` defaults to 16. User can adjust. Prevents OOM on long videos.
- **D-12b:** Save Video is an OUTPUT_NODE = True (terminal node, triggers video download and UI preview).
- **D-12c:** Video preview uses ComfyUI's OUTPUT_NODE + preview mechanism (gifs/video in UI canvas).
- **D-13:** ComfyUI IMAGE tensor (B,H,W,C float32 [0,1]) -> JPEG quality=95 -> base64 data URI for API upload.
  - Conversion: float32 -> uint8 via `np.clip(tensor * 255, 0, 255).astype(np.uint8)` -> PIL Image -> JPEG bytes -> base64 data URI.
  - Uses `data:image/jpeg;base64,{encoded}` format (matches test script `encode_image_to_base64` pattern).

### Claude's Discretion
- `api_client.py` I2V extension method (new `create_i2v_video` / `create_and_wait_i2v` functions or extend existing)
- Video download implementation (requests streaming to ComfyUI output directory)
- Frame extraction implementation details (opencv VideoCapture, frame skipping strategy)
- Save Video filename generation (timestamp/uuid/sequential)
- Save Video subfolder handling (create if not exists)
- I2V node parameter layout (grouping of image input + generation params)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| I2V-01 | User provides IMAGE tensor + prompt to generate video with reference image | I2V node accepts IMAGE as required input in INPUT_TYPES. Tensor-to-base64 conversion via D-13 pipeline. New `create_i2v_video` function adds `input` field to API payload. |
| I2V-02 | Image converted from ComfyUI tensor (B,H,W,C float32) to base64 JPEG data URI | Conversion: `np.clip(tensor * 255, 0, 255).astype(np.uint8)` -> PIL Image -> JPEG quality=95 -> base64 -> `data:image/jpeg;base64,{encoded}`. Verified in seedance_video.py pattern. |
| I2V-03 | Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING) | NOTE: CONTEXT.md D-10 overrides this. I2V outputs `(video_url: STRING, video_id: STRING)` only. first_frame extraction is Save Video's job per D-11. |
| I2V-04 | User can select resolution, aspect ratio, and duration same as T2V | I2V node reuses same INPUT_TYPES for resolution/ratio/duration as T2V node. Same SIZE_MAP applies. |
| VSAV-01 | Save Video node downloads generated video from URL to ComfyUI output directory | Uses `requests.get(url, stream=True)` with `iter_content(8192)`. Saves to `folder_paths.get_output_directory()`. Proven in seedance_video.py `download_video()`. |
| VSAV-02 | Node extracts frames and returns as ComfyUI IMAGE tensor with frame_load_cap | `cv2.VideoCapture` reads frames, converts BGR->RGB, stacks as numpy array, divides by 255.0 for float32 [0,1]. frame_load_cap defaults to 16 per D-12a. |
| VSAV-03 | Video preview displays in ComfyUI UI canvas | OUTPUT_NODE returns `{"ui": {"images": [{"filename": ..., "subfolder": ..., "type": "output"}]}}`. ComfyUI renders video/gif preview automatically for .mp4 files in output dir. |
| VSAV-04 | User can configure filename prefix and save subfolder | `filename_prefix` as STRING input (default "Seedance"). `subfolder` as STRING input. Uses `folder_paths.get_save_image_path()` for path resolution. |
</phase_requirements>

## Standard Stack

### Core (existing -- do NOT reinstall)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| requests | 2.32.5 | HTTP client for API + video download | Phase 1 proven. Streaming support for large video files. |
| numpy | 2.1.2 | Array conversion between tensor and image formats | Already installed with PyTorch. |
| Pillow | 11.0.0 | Tensor to JPEG encoding for API upload | Standard in ComfyUI ecosystem. JPEG quality=95 encoding. |
| pytest | 9.0.2 | Testing framework | Phase 1 proven. 36 tests passing. |
| torch | 2.5.1+cu121 | ComfyUI IMAGE tensor format | Already in ComfyUI environment. |

### New Dependencies (must install)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| opencv-python | >= 4.7 | Video frame extraction from downloaded .mp4 | Save Video node -- `cv2.VideoCapture` to read frames, BGR->RGB conversion |

**Installation:**
```bash
pip install opencv-python>=4.7
```

Note: `opencv-python` is already listed in `requirements.txt` from Phase 1 but is NOT currently installed in this environment. ComfyUI Manager would auto-install it. For local dev, run the pip command above.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| opencv-python | decord | decord is ~2x faster but an extra uncommon dependency. Speed difference is negligible for 4-15s videos. opencv is already in ComfyUI ecosystem. |
| requests streaming | urllib | urllib requires more boilerplate for streaming. requests is Phase 1 proven. |
| PIL JPEG encoding | turbojpeg | turbojpeg requires libturbojpeg system dependency. PIL JPEG quality=95 is portable and sufficient. |

## Architecture Patterns

### Recommended Project Structure
```
seedance_comfyui/
    __init__.py         # NODE_CLASS_MAPPINGS -- add I2V + Save Video entries
    api_client.py       # EXTEND with I2V functions (do NOT modify T2V functions)
    nodes.py            # ADD SeedanceImageToVideo + SeedanceSaveVideo classes
tests/
    conftest.py         # EXTEND with I2V-specific fixtures
    test_nodes.py       # ADD TestSeedanceImageToVideo + TestSeedanceSaveVideo
    test_api_client.py  # ADD test_create_i2v_video + test_create_and_wait_i2v
    test_registration.py # Will auto-pass once __init__.py is updated
```

### Pattern 1: Extending api_client.py with I2V Functions
**What:** Add new standalone functions for I2V alongside existing T2V functions. Do NOT modify existing `create_video`, `wait_for_video`, or `create_and_wait`.
**When to use:** I2V needs to pass image data in the `input` field of the API payload.
**Example:**
```python
# api_client.py -- NEW functions to ADD (do not modify existing)

def create_i2v_video(api_key, prompt, image_data_uri, duration=5, resolution="1080p", ratio="16:9"):
    """Submit an I2V task with image reference. Returns video ID string."""
    headers = _get_headers(api_key)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "seconds": duration,
        "input": image_data_uri,  # base64 data URI string
    }
    size = _get_size(resolution, ratio)
    if size:
        payload["size"] = size
    resp = requests.post(f"{BASE_URL}/videos", headers=headers, json=payload)
    _check_response(resp)
    data = resp.json()
    video_id = data.get("id") or data.get("video_id")
    if not video_id:
        raise RuntimeError(f"No video ID in response: {data}")
    return video_id


def create_and_wait_i2v(api_key, prompt, image_data_uri, duration=5, resolution="1080p", ratio="16:9"):
    """Create I2V and wait for completion. Returns result dict with video_url and video_id."""
    video_id = create_i2v_video(api_key, prompt, image_data_uri, duration, resolution, ratio)
    print(f"[Seedance] I2V video created: {video_id}")
    result = wait_for_video(api_key, video_id)
    print(f"[Seedance] I2V video completed: {result.get('video_url', 'N/A')}")
    video_url = result.get("video_url") or result.get("url", "")
    return {"video_url": video_url, "video_id": video_id}
```

### Pattern 2: ComfyUI IMAGE Tensor to Base64 Data URI
**What:** Convert ComfyUI IMAGE tensor (B,H,W,C float32 [0,1]) to JPEG base64 data URI for API upload.
**When to use:** I2V node's `generate()` method, before calling the API client.
**Example:**
```python
# nodes.py -- inside SeedanceImageToVideo.generate() or as a helper function
import base64
import io
import numpy as np
from PIL import Image

def _tensor_to_data_uri(tensor):
    """Convert ComfyUI IMAGE tensor to JPEG base64 data URI.

    tensor: shape (B, H, W, C) float32 in [0.0, 1.0]
    Returns: 'data:image/jpeg;base64,...' string (uses first image in batch)
    """
    # Take first image in batch, convert float32 [0,1] to uint8 [0,255]
    image_array = np.clip(tensor[0].cpu().numpy() * 255, 0, 255).astype(np.uint8)
    pil_image = Image.fromarray(image_array)
    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG", quality=95)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"
```

### Pattern 3: Save Video OUTPUT_NODE
**What:** Download video from URL, extract frames, save first frame as PNG, return IMAGE tensor + paths + UI preview dict.
**When to use:** Save Video node's `save()` method.
**Example:**
```python
# nodes.py -- SeedanceSaveVideo class structure
import os
import folder_paths  # ComfyUI built-in

class SeedanceSaveVideo:
    CATEGORY = "Seedance 2.0"
    OUTPUT_NODE = True  # Terminal node -- triggers download and preview

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {"default": ""}),
            },
            "optional": {
                "filename_prefix": ("STRING", {"default": "Seedance"}),
                "subfolder": ("STRING", {"default": ""}),
                "frame_load_cap": ("INT", {"default": 16, "min": 1, "max": 1000}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("frames", "first_frame_path", "video_path")
    FUNCTION = "save"

    def save(self, video_url, filename_prefix="Seedance", subfolder="", frame_load_cap=16):
        # 1. Resolve output directory
        output_dir = folder_paths.get_output_directory()
        target_dir = os.path.join(output_dir, subfolder) if subfolder else output_dir
        os.makedirs(target_dir, exist_ok=True)

        # 2. Download video via streaming
        # 3. Extract frames via cv2.VideoCapture
        # 4. Save first frame as PNG
        # 5. Build UI preview dict

        # Return format for ComfyUI OUTPUT_NODE:
        # result = (frames_tensor, first_frame_path, video_path)
        # ui_value = {"ui": {"images": [{"filename": ..., "subfolder": ..., "type": "output"}]}}
        # return {**dict(zip(self.RETURN_NAMES, result)), **ui_value}
        pass
```

### Pattern 4: Video Frame Extraction with OpenCV
**What:** Extract frames from downloaded .mp4 file as ComfyUI IMAGE tensors.
**When to use:** Save Video node, after downloading the video.
**Example:**
```python
import cv2
import numpy as np
import torch

def _extract_frames(video_path, frame_load_cap=16):
    """Extract frames from video file as ComfyUI IMAGE tensor.

    Returns: torch.Tensor of shape (N, H, W, C) float32 in [0.0, 1.0]
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    count = 0
    while count < frame_load_cap:
        ret, frame = cap.read()
        if not ret:
            break
        # OpenCV reads as BGR, convert to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Normalize to float32 [0, 1] for ComfyUI IMAGE format
        frame_float = frame_rgb.astype(np.float32) / 255.0
        frames.append(frame_float)
        count += 1
    cap.release()

    if not frames:
        raise RuntimeError("No frames extracted from video")

    # Stack into (N, H, W, C) tensor
    return torch.from_numpy(np.stack(frames, axis=0))
```

### Pattern 5: Video Download via Requests Streaming
**What:** Download video from URL to local file with streaming to handle large files.
**When to use:** Save Video node, before frame extraction.
**Example:**
```python
import requests

def _download_video(video_url, output_path):
    """Download video from URL to local file using streaming."""
    resp = requests.get(video_url, stream=True, timeout=300)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path
```

### Anti-Patterns to Avoid
- **Modifying existing T2V functions:** Do NOT change `create_video` or `create_and_wait` signatures. Add new parallel functions instead. Existing T2V tests must keep passing without modification.
- **Skipping the BGR->RGB conversion:** OpenCV reads frames in BGR order. ComfyUI expects RGB. Forgetting `cv2.cvtColor` produces color-swapped outputs.
- **Not handling batch dimension in tensor conversion:** ComfyUI IMAGE is (B,H,W,C). When converting to PIL for API upload, take `tensor[0]` (first image in batch).
- **Returning raw tuples from OUTPUT_NODE:** OUTPUT_NODEs must return a dict, not a tuple. Use `{"result": (values...), "ui": {...}}` or merge the output dict with ui dict.
- **Using VIDEO input type:** ComfyUI does not have a native VIDEO input type. Video URLs are passed as STRING. Only IMAGE tensor type exists for image data.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Video decoding | Custom byte parser for .mp4 frames | `cv2.VideoCapture` | MP4 container parsing is extremely complex. OpenCV handles variable frame rate, codecs, and edge cases. |
| Image encoding | Manual JPEG bit-level encoding | `PIL.Image.save(format="JPEG", quality=95)` | JPEG encoding involves DCT transforms, quantization, Huffman coding. PIL handles this correctly and efficiently. |
| Output path management | Custom path resolution logic | `folder_paths.get_output_directory()` + `os.path.join` | ComfyUI manages output directories with configurable paths. `folder_paths` is the canonical API. |
| Filename deduplication | Custom counter logic | `folder_paths.get_save_image_path()` | ComfyUI's built-in handles counter incrementing, subfolder creation, and conflict avoidance. Returns 5-tuple. |
| Auth header construction | Custom header builder | `_get_headers(api_key)` (existing) | Already proven in Phase 1. Reuse for all API calls including I2V. |

**Key insight:** ComfyUI provides `folder_paths` for all output directory management. The official `SaveImage` node in ComfyUI's `nodes.py` is the reference implementation for saving files and returning UI preview data.

## Common Pitfalls

### Pitfall 1: OpenCV Not Installed
**What goes wrong:** `import cv2` fails at runtime when Save Video node executes.
**Why it happens:** opencv-python is in requirements.txt but may not be installed in dev environments.
**How to avoid:** Ensure `pip install opencv-python>=4.7` is run. Add a defensive import with clear error message at module level.
**Warning signs:** ModuleNotFoundError for cv2 when importing nodes.py.

### Pitfall 2: OUTPUT_NODE Return Format
**What goes wrong:** ComfyUI does not display the video preview or crashes when executing the node.
**Why it happens:** OUTPUT_NODEs must return a dict, not a plain tuple. The dict must contain `"ui"` key with image entries for preview.
**How to avoid:** Return format must be: `{"ui": {"images": [{"filename": "x.mp4", "subfolder": "", "type": "output"}]}}` merged with output values. Study ComfyUI's `SaveImage` node pattern exactly.
**Warning signs:** Node executes but no preview appears in UI canvas.

### Pitfall 3: Tensor Batch Dimension
**What goes wrong:** API receives corrupted image data or wrong dimensions.
**Why it happens:** ComfyUI IMAGE tensor is (B, H, W, C). For I2V, we need only the first image: `tensor[0]` gives (H, W, C). Forgetting the batch index causes shape mismatch with PIL.
**How to avoid:** Always use `tensor[0]` before converting to PIL Image. Add an assertion for expected shape.
**Warning signs:** PIL raises TypeError or the API returns 400 errors.

### Pitfall 4: Video URL May Be Empty
**What goes wrong:** Save Video node crashes when `video_url` is empty string.
**Why it happens:** User wires the node incorrectly or the API returns no URL.
**How to avoid:** Validate `video_url` at the start of the `save()` method. Raise a clear ValueError with Chinese message.
**Warning signs:** `requests.get("")` raises MissingSchema error.

### Pitfall 5: Frame Extraction on Empty/Corrupt Video
**What goes wrong:** `cv2.VideoCapture` opens but reads 0 frames from a corrupt or empty download.
**Why it happens:** Network error during download, disk full, or API returned an error page instead of video data.
**How to avoid:** Check `cap.isOpened()` after creating VideoCapture. Check that frames list is non-empty after the read loop. Raise RuntimeError with clear message if no frames.
**Warning signs:** Empty frames list, tensor shape (0, H, W, C).

### Pitfall 6: Mock Patch Target for I2V Tests
**What goes wrong:** `@patch("seedance_comfyui.api_client.create_i2v_video")` does not intercept calls from `nodes.py`.
**Why it happens:** Phase 1 established the pattern: mock the function in the *caller's* namespace. If `nodes.py` imports `create_and_wait_i2v`, the patch target must be `seedance_comfyui.nodes.create_and_wait_i2v` (same as T2V pattern where target is `seedance_comfyui.nodes.create_and_wait`).
**How to avoid:** Follow Phase 1 pattern exactly. Patch at `seedance_comfyui.nodes.create_and_wait_i2v`, NOT at `seedance_comfyui.api_client.create_and_wait_i2v`.
**Warning signs:** Mock.assert_called_once() fails, or the real API gets called during tests.

## Code Examples

### Complete I2V Node Class
```python
# Source: Based on Phase 1 SeedanceTextToVideo pattern + CONTEXT.md D-10/D-13
import base64
import io

import numpy as np
from PIL import Image

from .api_client import create_and_wait_i2v


class SeedanceImageToVideo:
    """Image-to-video generation node using Seedance 2.0 via AIHubMix."""

    CATEGORY = "Seedance 2.0"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # ComfyUI IMAGE tensor
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
        # Convert IMAGE tensor to base64 data URI per D-13
        image_array = np.clip(image[0].cpu().numpy() * 255, 0, 255).astype(np.uint8)
        pil_image = Image.fromarray(image_array)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=95)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{encoded}"

        result = create_and_wait_i2v(api_key, prompt, data_uri, duration, resolution, ratio)
        return (result["video_url"], result["video_id"])
```

### Complete Save Video Node Class
```python
# Source: Based on ComfyUI official SaveImage pattern + CONTEXT.md D-12
import os
import uuid

import cv2
import folder_paths
import numpy as np
import requests
import torch


class SeedanceSaveVideo:
    """Download video, extract frames, save first frame, enable UI preview."""

    CATEGORY = "Seedance 2.0"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {"default": ""}),
            },
            "optional": {
                "filename_prefix": ("STRING", {"default": "Seedance"}),
                "subfolder": ("STRING", {"default": ""}),
                "frame_load_cap": ("INT", {"default": 16, "min": 1, "max": 1000}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("frames", "first_frame_path", "video_path")
    FUNCTION = "save"

    def save(self, video_url, filename_prefix="Seedance", subfolder="", frame_load_cap=16):
        if not video_url:
            raise ValueError(
                "视频链接不能为空。请将视频生成节点连接到此节点。"
            )

        # Resolve output directory
        output_dir = folder_paths.get_output_directory()
        target_dir = os.path.join(output_dir, subfolder) if subfolder else output_dir
        os.makedirs(target_dir, exist_ok=True)

        # Generate unique filename
        unique_id = uuid.uuid4().hex[:8]
        video_filename = f"{filename_prefix}_{unique_id}.mp4"
        video_path = os.path.join(target_dir, video_filename)

        # Download video
        print(f"[Seedance] Downloading video to {video_path}...")
        resp = requests.get(video_url, stream=True, timeout=300)
        resp.raise_for_status()
        with open(video_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract frames
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"无法打开视频文件: {video_path}")
        frames = []
        while len(frames) < frame_load_cap:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb.astype(np.float32) / 255.0)
        cap.release()

        if not frames:
            raise RuntimeError("未能从视频中提取任何帧")

        frames_tensor = torch.from_numpy(np.stack(frames, axis=0))

        # Save first frame as PNG
        first_frame = (frames[0] * 255).astype(np.uint8)
        from PIL import Image as PILImage
        first_frame_filename = f"{filename_prefix}_{unique_id}_first_frame.png"
        first_frame_path = os.path.join(target_dir, first_frame_filename)
        PILImage.fromarray(first_frame).save(first_frame_path)

        # Build UI preview -- return video file for ComfyUI canvas preview
        ui_images = [{
            "filename": video_filename,
            "subfolder": subfolder,
            "type": "output",
        }]

        return {
            "ui": {"images": ui_images},
            "result": (frames_tensor, first_frame_path, video_path),
        }
```

### __init__.py Update Pattern
```python
# Source: Phase 1 __init__.py pattern -- extend with new node classes
from .nodes import (
    SeedanceApiKey,
    SeedanceTextToVideo,
    SeedanceImageToVideo,
    SeedanceSaveVideo,
)

NODE_CLASS_MAPPINGS = {
    "SeedanceApiKey": SeedanceApiKey,
    "SeedanceTextToVideo": SeedanceTextToVideo,
    "SeedanceImageToVideo": SeedanceImageToVideo,
    "SeedanceSaveVideo": SeedanceSaveVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceApiKey": "Seedance 2.0 API Key",
    "SeedanceTextToVideo": "Seedance 2.0 Text to Video",
    "SeedanceImageToVideo": "Seedance 2.0 Image to Video",
    "SeedanceSaveVideo": "Seedance 2.0 Save Video",
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Video download via API content endpoint | Direct video_url download | Phase 1 API returns `video_url` in response | Use the URL directly, not `/v1/videos/{id}/content` |
| Manual frame counting with FPS | cv2.VideoCapture read loop | Standard opencv pattern | Simpler and handles variable frame rate |
| Tuple return from OUTPUT_NODE | Dict return with "ui" key | ComfyUI convention | OUTPUT_NODEs must return dict with "ui" for preview |

**Deprecated/outdated:**
- `VIDEO` ComfyUI input type: Does not exist. Video URLs are STRING inputs.
- `/v1/videos/{id}/content` endpoint for download: Phase 1 API returns `video_url` directly. Use that URL instead of constructing a content endpoint URL.

## Open Questions

1. **ComfyUI mp4 preview behavior**
   - What we know: ComfyUI's official SaveImage node returns PNG images in `ui.images`. The UI renders these as previews.
   - What's unclear: Whether ComfyUI automatically previews .mp4 files the same way, or if additional configuration is needed for video preview in the canvas.
   - Recommendation: Return the video file in `ui.images` with `"type": "output"`. If ComfyUI does not auto-preview .mp4, the first frame PNG will serve as the preview. The video file is always saved to disk regardless of preview behavior.

2. **AIHubMix video_url format (redirect vs direct)**
   - What we know: STATE.md notes this as a concern from Phase 3 planning. The test script uses `requests.get(url, stream=True)` which follows redirects by default.
   - What's unclear: Whether the URL is a direct link (200 with bytes) or a redirect (302 to CDN).
   - Recommendation: `requests.get(stream=True)` handles both cases transparently. No special handling needed.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime | Yes | 3.11.9 | -- |
| requests | API calls + download | Yes | 2.32.5 | -- |
| numpy | Tensor conversion | Yes | 2.1.2 | -- |
| Pillow | JPEG encoding | Yes | 11.0.0 | -- |
| torch | ComfyUI tensors | Yes | 2.5.1+cu121 | -- |
| pytest | Testing | Yes | 9.0.2 | -- |
| opencv-python | Frame extraction | No | -- | Must install: `pip install opencv-python>=4.7` |
| folder_paths | Output directory | No (ComfyUI module) | -- | Mock in tests; available at runtime in ComfyUI |

**Missing dependencies with no fallback:**
- `opencv-python`: Required for Save Video frame extraction. Must be installed before testing Save Video node. Listed in requirements.txt but not yet installed in dev environment.
- `folder_paths`: ComfyUI built-in module. Not available outside ComfyUI runtime. Must be mocked in unit tests.

**Missing dependencies with fallback:**
- None -- all other dependencies are confirmed available.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | None (auto-discovery) |
| Quick run command | `python -m pytest tests/ -x --tb=short -q` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| I2V-01 | I2V node accepts IMAGE + prompt inputs | unit | `python -m pytest tests/test_nodes.py::TestSeedanceImageToVideo -x` | Wave 0 |
| I2V-02 | Tensor-to-base64 JPEG conversion | unit | `python -m pytest tests/test_nodes.py::TestSeedanceImageToVideo::test_i2v_tensor_conversion -x` | Wave 0 |
| I2V-03 | I2V outputs (video_url, video_id) | unit | `python -m pytest tests/test_nodes.py::TestSeedanceImageToVideo::test_i2v_output_types -x` | Wave 0 |
| I2V-04 | I2V resolution/ratio/duration params | unit | `python -m pytest tests/test_nodes.py::TestSeedanceImageToVideo::test_i2v_size_options -x` | Wave 0 |
| VSAV-01 | Video download to output directory | unit | `python -m pytest tests/test_nodes.py::TestSeedanceSaveVideo::test_save_downloads_video -x` | Wave 0 |
| VSAV-02 | Frame extraction with frame_load_cap | unit | `python -m pytest tests/test_nodes.py::TestSeedanceSaveVideo::test_save_extracts_frames -x` | Wave 0 |
| VSAV-03 | OUTPUT_NODE ui preview dict | unit | `python -m pytest tests/test_nodes.py::TestSeedanceSaveVideo::test_save_ui_preview -x` | Wave 0 |
| VSAV-04 | Filename prefix and subfolder config | unit | `python -m pytest tests/test_nodes.py::TestSeedanceSaveVideo::test_save_custom_prefix -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x --tb=short -q`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_nodes.py` -- Add `TestSeedanceImageToVideo` class (INPUT_TYPES, RETURN_TYPES, mock generate, tensor conversion)
- [ ] `tests/test_nodes.py` -- Add `TestSeedanceSaveVideo` class (INPUT_TYPES, RETURN_TYPES, OUTPUT_NODE, mock download + frame extraction)
- [ ] `tests/test_api_client.py` -- Add `test_create_i2v_video` and `test_create_and_wait_i2v` functions
- [ ] `tests/conftest.py` -- Add I2V-specific fixtures (mock_i2v_response, sample_image_tensor)
- [ ] opencv-python install: `pip install opencv-python>=4.7` -- needed for Save Video frame extraction tests
- [ ] `folder_paths` mock -- needed in tests since ComfyUI module not available outside runtime

## Sources

### Primary (HIGH confidence)
- Existing `api_client.py` -- Phase 1 proven patterns, function signatures, SIZE_MAP, error handling
- Existing `nodes.py` -- Phase 1 node class structure pattern
- `seedance_video.py` -- Proven test script with I2V pattern (`input` field), download pattern, base64 encoding
- ComfyUI Official `nodes.py` (SaveImage class) -- OUTPUT_NODE pattern, `folder_paths` usage, UI preview dict format
- ComfyUI Official Docs - Tensors: https://docs.comfy.org/custom-nodes/backend/tensors -- IMAGE format [B,H,W,C] float32

### Secondary (MEDIUM confidence)
- AIHubMix API Docs: https://docs.aihubmix.com/en/api/Video-Gen -- I2V uses same POST /v1/videos endpoint with `input` field
- ComfyUI Official Docs - Custom Node Walkthrough: https://docs.comfy.org/custom-nodes/walkthrough -- NODE_CLASS_MAPPINGS registration

### Tertiary (LOW confidence)
- ComfyUI .mp4 preview behavior -- assumed based on OUTPUT_NODE pattern but not verified with a running ComfyUI instance

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries verified installed or listed in requirements.txt. Versions confirmed via pip.
- Architecture: HIGH -- patterns proven in Phase 1, extended for I2V. ComfyUI OUTPUT_NODE pattern verified from official source.
- Pitfalls: HIGH -- based on Phase 1 experience (mock patch target) and well-known opencv/color-space gotchas.

**Research date:** 2026-04-03
**Valid until:** 2026-05-03 (stable domain -- ComfyUI API and opencv patterns are mature)

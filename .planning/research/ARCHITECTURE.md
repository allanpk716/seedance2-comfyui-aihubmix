# Architecture Patterns

**Domain:** ComfyUI Custom Node Plugin for Video Generation (Seedance 2.0 via AIHubMix API)
**Researched:** 2026-04-03

## Recommended Architecture

The plugin follows the standard ComfyUI custom node pattern: a Python package in `custom_nodes/` that exports `NODE_CLASS_MAPPINGS` from `__init__.py`. The architecture separates concerns into four layers: registration, API client, node classes, and image conversion utilities.

```
custom_nodes/seedance_comfyui/
    __init__.py                  # Registration: exports NODE_CLASS_MAPPINGS
    seedance_api.py              # API client: all AIHubMix HTTP interactions
    seedance_nodes.py            # Node classes: T2V, I2V, Extend, Omni, ApiKey
    seedance_video_saver.py      # Video saver node: download + frame extraction
    requirements.txt             # Dependencies: requests, opencv-python, Pillow
```

### Component Boundaries

| Component | File | Responsibility | Communicates With |
|-----------|------|---------------|-------------------|
| **Registration** | `__init__.py` | Discovers and exports node classes to ComfyUI. Merges `NODE_CLASS_MAPPINGS` from node modules. | ComfyUI runtime (loaded on startup) |
| **API Client** | `seedance_api.py` | All HTTP communication with AIHubMix. Create video, poll status, download content, image encoding. | Node classes (called by their `run()` methods) |
| **Generation Nodes** | `seedance_nodes.py` | 5 node classes that define inputs/outputs for ComfyUI and orchestrate API calls. | API Client (delegates HTTP), ComfyUI (returns tensors/strings) |
| **Video Saver Node** | `seedance_video_saver.py` | Downloads completed video, saves to disk, extracts frames as IMAGE tensor, generates preview. | ComfyUI output directory, AIHubMix download endpoint |
| **Dependencies** | `requirements.txt` | Declares `requests`, `opencv-python`, `Pillow`. No exotic deps. | pip / ComfyUI Manager |

### Data Flow

```
User workflow in ComfyUI canvas:

[ApiKey Node] --api_key (STRING)--> [T2V / I2V / Omni Node]
                                        |
                                        v
                               seedance_api.py
                                  |          |
                     POST /v1/videos    GET /v1/videos/{id} (poll loop)
                                  |          |
                                  v          v
                              AIHubMix API (cloud)
                                  |
                                  v
                         video_url (STRING)
                         first_frame (IMAGE tensor)
                         request_id (STRING)
                                  |
                                  v
                          [Video Saver Node]
                                  |
                        GET /v1/videos/{id}/content
                                  |
                                  v
                    Save .mp4 to output/seedance/
                    Return frames as IMAGE tensor
                    Return filepath (STRING)
                    Return frame_count (INT)
                    UI preview via {"ui": {"gifs": [...]}}
```

### Detailed Data Flow by Operation

**Text-to-Video:**
1. User enters prompt, resolution, ratio, duration in T2V node
2. Node calls `seedance_api.create_video()` which POSTs to `/v1/videos`
3. API returns `video_id` immediately
4. Node calls `seedance_api.poll_until_complete()` which loops GET `/v1/videos/{id}`
5. On completion, node extracts `video_url` from response
6. Node extracts first frame via opencv, returns as IMAGE tensor
7. Returns tuple: `(video_url: str, first_frame: Tensor, request_id: str)`

**Image-to-Video:**
1. User connects IMAGE tensor(s) from LoadImage or other nodes
2. Node converts each IMAGE tensor to base64 data URI via `seedance_api.tensor_to_data_uri()`
3. Data URI is placed directly in the `input` field of the API payload (no separate upload step needed with AIHubMix)
4. Same poll and return pattern as T2V

**Video Extend:**
1. User connects `request_id` output from a completed generation node
2. Node calls extend endpoint with the `request_id`
3. Same poll and return pattern

**Omni Reference:**
1. User provides IMAGE tensors, video URLs, and/or audio URLs
2. IMAGE tensors are converted to base64 data URIs inline
3. All references combined in a single API payload
4. Same poll and return pattern

**Video Save:**
1. User connects `video_url` from a generation node
2. Node downloads via GET `/v1/videos/{id}/content`
3. Saves to `output/seedance/` subfolder with auto-incrementing filename
4. Extracts frames via opencv, returns as IMAGE tensor batch
5. Returns UI preview via `{"ui": {"gifs": [{"filename": ..., "subfolder": ..., "type": "output", "format": "video/mp4"}]}}`

## Patterns to Follow

### Pattern 1: API Client Singleton Module (Not a Class)
**What:** Use a module-level collection of functions (`seedance_api.py`) rather than a class instance for the API client.
**When:** Always -- the API base URL and model ID are constants, and functions are simpler than managing class state.
**Why:** ComfyUI instantiates node classes on every execution. If the API client were a class, you would need to re-instantiate it each time. Module-level functions with the API key passed as a parameter are stateless and avoid initialization overhead.
**Example:**
```python
# seedance_api.py
BASE_URL = "https://aihubmix.com/v1"
MODEL = "doubao-seedance-2-0-260128"

def create_video(api_key: str, prompt: str, seconds: int = 5, size: str = None, input_ref: str = None) -> str:
    """Submit video generation. Returns video_id."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "prompt": prompt, "seconds": seconds}
    if size:
        payload["size"] = size
    if input_ref:
        payload["input"] = input_ref
    resp = requests.post(f"{BASE_URL}/videos", headers=headers, json=payload)
    _check_response(resp)
    return resp.json()["id"]

def poll_until_complete(api_key: str, video_id: str, interval: int = 5, max_wait: int = 900) -> dict:
    """Block until video is completed or failed. Returns full result dict."""
    ...

def download_video(api_key: str, video_id: str, output_path: str) -> str:
    """Download video content to disk. Returns filepath."""
    ...

def tensor_to_data_uri(tensor: torch.Tensor) -> str:
    """Convert ComfyUI IMAGE tensor [B,H,W,C] to data:image/jpeg;base64,..."""
    ...
```

### Pattern 2: Synchronous Polling with time.sleep()
**What:** Block the node's `run()` method with a polling loop and `time.sleep(interval)`.
**When:** All generation nodes. ComfyUI node execution is inherently synchronous -- each node blocks until it returns.
**Why:** ComfyUI executes nodes sequentially on the execution thread. There is no benefit to async because the workflow engine waits for the node to return anyway. The reference project and other API-based video nodes (Kling, Sora) all use this pattern. Using `asyncio` would add complexity without any throughput gain since ComfyUI does not run multiple nodes concurrently for a single prompt execution.
**Example:**
```python
def poll_until_complete(api_key: str, video_id: str, interval: int = 5, max_wait: int = 900) -> dict:
    headers = {"Authorization": f"Bearer {api_key}"}
    deadline = time.time() + max_wait
    while time.time() < deadline:
        resp = requests.get(f"{BASE_URL}/videos/{video_id}", headers=headers)
        _check_response(resp)
        data = resp.json()
        status = data.get("status", "queued")
        if status == "completed":
            return data
        if status == "failed":
            raise RuntimeError(f"Video generation failed: {data.get('error', 'unknown')}")
        time.sleep(interval)
    raise RuntimeError(f"Timeout waiting for video {video_id}")
```

### Pattern 3: Node Class with INPUT_TYPES / RETURN_TYPES / FUNCTION
**What:** Each node is a Python class with four required class attributes and one instance method.
**When:** Every node definition.
**Why:** This is the ComfyUI contract. ComfyUI inspects these attributes to build the UI, validate connections, and execute the node.
**Example:**
```python
class SeedanceTextToVideo:
    CATEGORY = "Seedance 2.0"              # Menu location in ComfyUI
    FUNCTION = "run"                        # Method name to call

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "resolution": (["480p", "720p", "1080p"], {"default": "1080p"}),
                "ratio": (["16:9", "9:16", "4:3", "3:4", "1:1", "21:9"], {"default": "16:9"}),
                "duration": ("INT", {"default": 5, "min": 4, "max": 15}),
            },
            "optional": {
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("video_url", "first_frame", "request_id")

    def run(self, prompt, resolution, ratio, duration, api_key=""):
        api_key = _resolve_api_key(api_key)
        size = _get_size(resolution, ratio)
        video_id = seedance_api.create_video(api_key, prompt, duration, size)
        result = seedance_api.poll_until_complete(api_key, video_id)
        video_url = result.get("url") or result["content_url"]
        first_frame = seedance_api.extract_first_frame(video_url)
        return (video_url, first_frame, video_id)
```

### Pattern 4: Inline Image Encoding (No Separate Upload)
**What:** Convert ComfyUI IMAGE tensors directly to base64 data URIs and include them in the API request body.
**When:** I2V and Omni nodes.
**Why:** AIHubMix supports inline base64/URL input in the `input` field directly. The reference project (muapi.ai) required a separate `POST /upload_file` step to get a URL first. AIHubMix eliminates this step, simplifying the architecture.
**Example:**
```python
def tensor_to_data_uri(tensor: torch.Tensor) -> str:
    """ComfyUI IMAGE [1,H,W,C] float32 [0,1] -> data:image/jpeg;base64,..."""
    if tensor.dim() == 4:
        tensor = tensor[0]  # Take first in batch: [H,W,C]
    arr = (tensor.cpu().numpy() * 255).astype("uint8")
    img = Image.fromarray(arr, "RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"
```

### Pattern 5: OUTPUT_NODE with UI Preview
**What:** The Video Saver node sets `OUTPUT_NODE = True` and returns a dict with both `"ui"` and `"result"` keys.
**When:** The video saver node (the terminal node in the workflow that displays the video preview).
**Why:** ComfyUI renders the `"ui"` content in the node's preview area. The `"gifs"` key triggers the built-in video preview widget.
**Example:**
```python
class SeedanceVideoSaver:
    OUTPUT_NODE = True
    # ...
    def run(self, video_url, save_subfolder, filename_prefix, ...):
        # Download and save the video
        filepath = seedance_api.download_video(api_key, video_id, output_path)
        frames = self._extract_frames(filepath)
        filename = os.path.basename(filepath)
        preview = {
            "filename": filename,
            "subfolder": save_subfolder,
            "type": "output",
            "format": "video/mp4",
        }
        return {
            "ui": {"gifs": [preview]},
            "result": (frames, filepath, frames.shape[0])
        }
```

### Pattern 6: Size Resolution Mapping
**What:** Map human-friendly resolution/ratio pairs to pixel dimensions. Use `None` for 1080p to let the API default.
**When:** T2V and I2V nodes (any node that specifies video resolution).
**Why:** The AIHubMix API uses pixel dimensions in the `size` field (e.g., `"1280x720"`), but users think in terms of resolution tier + aspect ratio. The test script already has a proven mapping table. 1080p is the API default when `size` is omitted, which simplifies the most common case.
**Example:**
```python
SIZE_MAP = {
    ("480p", "16:9"): "832x480",
    ("480p", "9:16"): "480x832",
    ("480p", "1:1"):  "624x624",
    ("480p", "4:3"):  "640x480",
    ("480p", "3:4"):  "480x640",
    ("480p", "21:9"): "1120x480",
    ("720p", "16:9"): "1280x720",
    ("720p", "9:16"): "720x1280",
    ("720p", "1:1"):  "960x960",
    ("720p", "4:3"):  "960x720",
    ("720p", "3:4"):  "720x960",
    ("720p", "21:9"): "1680x720",
    # 1080p: return None (API default)
}

def get_size(resolution: str, ratio: str) -> str | None:
    if resolution == "1080p":
        return None
    return SIZE_MAP.get((resolution, ratio))
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: API Client as a ComfyUI Node
**What:** Making the API wrapper itself a node class that ComfyUI instantiates.
**Why bad:** ComfyUI manages node class lifecycles. API client state (like session objects) would be lost between executions. Node classes should only define the ComfyUI interface; the actual API logic belongs in a plain Python module.
**Instead:** Use a standalone module (`seedance_api.py`) with regular functions. Nodes import and call these functions.

### Anti-Pattern 2: Storing API Keys in Node Class State
**What:** Setting `self.api_key = api_key` on a node instance and expecting it to persist.
**Why bad:** ComfyUI may instantiate node classes fresh for each execution. There is no guarantee of state persistence between runs.
**Instead:** Pass the API key through the node graph via STRING connections (ApiKey Node output -> generation node input).

### Anti-Pattern 3: asyncio for API Polling
**What:** Using `asyncio.sleep()` or `aiohttp` for the polling loop inside a node's `run()` method.
**Why bad:** ComfyUI's execution engine is synchronous. The `run()` method is called in a synchronous context. Adding asyncio would require running an event loop inside a sync function (via `asyncio.run()`), which adds complexity and can conflict with ComfyUI's own event loop if it uses one.
**Instead:** Use `requests` with `time.sleep()`. This is the standard pattern used by all API-based ComfyUI custom nodes.

### Anti-Pattern 4: Separate Image Upload Step (muapi.ai Pattern)
**What:** Uploading images to a separate endpoint first to get a URL, then using that URL in the video generation request.
**Why bad:** This was necessary for muapi.ai but AIHubMix supports inline base64 data URIs in the request body. A separate upload step adds latency, complexity, and an extra failure point.
**Instead:** Encode IMAGE tensors directly to base64 data URIs and include them in the `input` field of the creation request.

### Anti-Pattern 5: Monolithic Single-File Plugin
**What:** Putting all node classes, API logic, and helpers in one large Python file.
**Why bad:** As the plugin grows (already 7+ nodes and helpers in the reference), a single file becomes hard to navigate. Testing individual functions becomes harder.
**Instead:** Separate into `seedance_api.py` (HTTP layer), `seedance_nodes.py` (generation nodes), `seedance_video_saver.py` (output node). `__init__.py` only handles registration.

### Anti-Pattern 6: Returning Latent Instead of IMAGE
**What:** Trying to return video data as LATENT type for downstream processing.
**Why bad:** Video generation APIs produce pixel-level video files, not diffusion model latents. Converting to LATENT would require a VAE encoder, which adds enormous complexity and is unnecessary. Users who want to do further processing can use existing ComfyUI nodes to convert.
**Instead:** Return STRING (video_url), IMAGE (first_frame or all frames), and STRING (request_id).

## Node Class Design

### Recommended Nodes (v1 Scope)

| Node | Inputs | Outputs | API Endpoint | Category |
|------|--------|---------|-------------|----------|
| **ApiKey** | `api_key` (STRING) | `api_key` (STRING) | N/A (pass-through) | Seedance 2.0 |
| **TextToVideo** | prompt, resolution, ratio, duration, api_key (opt) | video_url, first_frame, request_id | `POST /v1/videos` | Seedance 2.0 |
| **ImageToVideo** | prompt, image_1 (IMAGE), resolution, ratio, duration, api_key (opt) | video_url, first_frame, request_id | `POST /v1/videos` | Seedance 2.0 |
| **Extend** | request_id, duration, api_key (opt), prompt (opt) | video_url, first_frame, new_request_id | `POST /v1/videos` (extend payload) | Seedance 2.0 |
| **Omni** | prompt, image_1..9, video_url_1..3, audio_url_1..3, resolution, ratio, duration, api_key (opt) | video_url, first_frame, request_id | `POST /v1/videos` | Seedance 2.0 |
| **VideoSaver** | video_url, save_subfolder, filename_prefix, frame_load_cap (opt), skip_first_frames (opt), select_every_nth (opt) | frames (IMAGE), filepath (STRING), frame_count (INT) | `GET /v1/videos/{id}/content` | Seedance 2.0 |

### Key Differences from Reference (muapi.ai -> AIHubMix)

| Aspect | Reference (muapi.ai) | This Plugin (AIHubMix) |
|--------|----------------------|----------------------|
| Auth header | `x-api-key` | `Authorization: Bearer` |
| Create endpoint | Separate per type: `/seedance-v2.0-t2v`, `/seedance-v2.0-i2v`, etc. | Unified: `POST /v1/videos` with `model` field |
| Poll endpoint | `GET /api/v1/predictions/{id}/result` | `GET /v1/videos/{id}` |
| Download | URL from result object | `GET /v1/videos/{id}/content` |
| Image upload | Separate `POST /api/v1/upload_file` step | Inline base64/URL in `input` field |
| Status values | `completed` / `failed` | `completed` / `failed` / `queued` / `in_progress` |
| Progress | Not provided | `progress` field (0-100 percentage) |

### Out-of-Scope Nodes (Defer to v2)

| Node | Why Deferred |
|------|-------------|
| **Character** | Multi-step pipeline (upload photos, generate character sheet, get character_id). Complex error handling. |
| **ConsistentVideo** | Depends on Character node. Requires character sheet management. |

## Image Conversion Pipeline

### ComfyUI to API (IMAGE tensor -> base64 data URI)

```
ComfyUI IMAGE tensor [B,H,W,C] float32 [0.0, 1.0]
    |
    v  (select batch[0])
[H,W,C] float32 [0.0, 1.0]
    |
    v  (* 255, astype uint8)
[H,W,C] uint8 [0, 255]
    |
    v  (PIL Image.fromarray)
PIL.Image RGB
    |
    v  (save to BytesIO as JPEG quality=95)
bytes
    |
    v  (base64.b64encode)
data:image/jpeg;base64,/9j/4AAQ...
```

### API to ComfyUI (video URL -> IMAGE tensor)

```
video_url (STRING from generation node)
    |
    v  (requests.get, stream=True, save to temp .mp4)
local .mp4 file
    |
    v  (cv2.VideoCapture, read frames)
BGR numpy arrays [H,W,3] uint8
    |
    v  (cv2.cvtColor BGR2RGB)
RGB numpy arrays [H,W,3] uint8
    |
    v  (astype float32 / 255.0)
float32 [0.0, 1.0]
    |
    v  (torch.from_numpy, stack, unsqueeze)
[B,H,W,C] torch.float32 tensor
```

### First Frame Extraction (for generation node output)

```
video_url (STRING)
    |
    v  (requests.get, save to temp file)
    |
    v  (cv2.VideoCapture, read single frame)
    |
    v  (same BGR->RGB->float32->tensor pipeline)
    |
    v
[1,H,W,C] torch.float32 IMAGE tensor (returned as first_frame output)
```

## File Structure for ComfyUI Manager Compatibility

```
seedance_comfyui/                   # Git repo root / custom_nodes subdirectory
    __init__.py                     # MUST export NODE_CLASS_MAPPINGS
    seedance_api.py                 # API client functions
    seedance_nodes.py               # Generation node classes
    seedance_video_saver.py         # Video saver node class
    requirements.txt                # pip dependencies
    README.md                       # Installation instructions
    LICENSE                         # MIT
    .gitignore                      # Exclude __pycache__, .env, etc.
```

### __init__.py Registration Pattern

```python
from .seedance_nodes import (
    SeedanceApiKey,
    SeedanceTextToVideo,
    SeedanceImageToVideo,
    SeedanceExtend,
    SeedanceOmni,
)
from .seedance_video_saver import SeedanceVideoSaver

NODE_CLASS_MAPPINGS = {
    "SeedanceApiKey": SeedanceApiKey,
    "SeedanceTextToVideo": SeedanceTextToVideo,
    "SeedanceImageToVideo": SeedanceImageToVideo,
    "SeedanceExtend": SeedanceExtend,
    "SeedanceOmni": SeedanceOmni,
    "SeedanceVideoSaver": SeedanceVideoSaver,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceApiKey": "Seedance 2.0 API Key",
    "SeedanceTextToVideo": "Seedance 2.0 Text-to-Video",
    "SeedanceImageToVideo": "Seedance 2.0 Image-to-Video",
    "SeedanceExtend": "Seedance 2.0 Extend",
    "SeedanceOmni": "Seedance 2.0 Omni Reference",
    "SeedanceVideoSaver": "Seedance 2.0 Save Video",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
```

### ComfyUI Manager Installation

Users install via:
1. ComfyUI Manager -> Install via Git URL -> `https://github.com/<user>/seedance_comfyui`
2. Manager runs `git clone` into `custom_nodes/seedance_comfyui/`
3. Manager runs `pip install -r requirements.txt`
4. User restarts ComfyUI

To list in ComfyUI Manager's searchable registry, submit a PR adding the repo to `custom-node-list.json` in the ComfyUI-Manager repository.

## Scalability Considerations

| Concern | At 1 user | At 100 users (shared server) | At scale |
|---------|-----------|------------------------------|----------|
| API rate limits | Not a concern | Add retry with exponential backoff on 429 | Queue system with rate limiter |
| Polling interval | 5s is fine | 5s fine; consider 3s for faster feedback | Configurable interval |
| Memory (frame extraction) | Frames fit in RAM | Limit `frame_load_cap` default to ~300 | Stream frames to disk |
| Timeout | 900s max wait | 900s adequate for most jobs | Make configurable per node |
| Concurrent requests | N/A (ComfyUI serial) | Each prompt runs serially within ComfyUI | External orchestration |

**Note:** ComfyUI executes nodes sequentially within a single prompt. Parallelism comes from users running multiple prompts. The plugin does not need to handle concurrent requests within a single execution.

## Suggested Build Order

The components have these dependencies:

```
1. seedance_api.py          -- no dependencies on other project files
   (can be tested standalone with the existing test script pattern)

2. seedance_nodes.py        -- depends on seedance_api.py
   (each node class is independent of the others)

3. seedance_video_saver.py  -- depends on seedance_api.py (download only)
   (independent of seedance_nodes.py)

4. __init__.py              -- depends on all node modules being complete
   (pure registration, no logic)

5. requirements.txt         -- no code dependencies
   (can be written at any time)

6. README.md                -- depends on final node names and structure
```

**Recommended implementation order:**

1. **seedance_api.py** first -- this is the foundation. Build and test the HTTP layer independently using the existing `seedance_video.py` test script as a reference.
2. **seedance_nodes.py** next -- implement ApiKey node first (trivial), then T2V (simplest generation), then I2V (adds image conversion), then Extend (reuses patterns), then Omni (most complex).
3. **seedance_video_saver.py** -- can be built in parallel with step 2 since it only depends on the API client.
4. **__init__.py** -- wire everything together once all node classes exist.
5. **README.md + requirements.txt + .gitignore** -- packaging and documentation.

## Sources

- [ComfyUI Official Docs - Getting Started (Custom Nodes)](https://docs.comfy.org/custom-nodes/walkthrough) -- HIGH confidence, official documentation
- [ComfyUI Official Docs - Lifecycle](https://docs.comfy.org/custom-nodes/backend/lifecycle) -- HIGH confidence, explains NODE_CLASS_MAPPINGS registration
- [ComfyUI Official Docs - Datatypes](https://docs.comfy.org/custom-nodes/backend/datatypes) -- HIGH confidence, IMAGE tensor format [B,H,W,C]
- [AIHubMix Video Generation API Docs](https://docs.aihubmix.com/en/api/Video-Gen) -- HIGH confidence, official API documentation
- [Reference Project: Anil-matcha/seedance2-comfyui](https://github.com/Anil-matcha/seedance2-comfyui) -- HIGH confidence, full source code reviewed
- [ComfyUI Manager - Publishing](https://docs.comfy.org/zh/custom-nodes/backend/manager) -- HIGH confidence, official publishing guide
- [ComfyUI Blog - Dependency Resolution](https://blog.comfy.org/p/dependency-resolution-and-custom) -- MEDIUM confidence, best practices for dependency management
- [ComfyScript VHS VideoCombine](https://github.com/Chaoses-Ib/ComfyScript/issues/22) -- HIGH confidence, shows OUTPUT_NODE ui format for video preview
- [Existing test script seedance_video.py](file:///C:/WorkSpace/seedance_comfyui/seedance_video.py) -- HIGH confidence, validates AIHubMix API interaction pattern

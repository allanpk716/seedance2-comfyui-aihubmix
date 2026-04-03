# Phase 1: Foundation + Text-to-Video - Research

**Researched:** 2026-04-03
**Domain:** ComfyUI Custom Node Development + AIHubMix Video Generation API
**Confidence:** HIGH

## Summary

Phase 1 builds the core plugin infrastructure: ComfyUI registration via `__init__.py`, an AIHubMix API client module, an API Key passthrough node, and a Text-to-Video generation node. The primary technical references are the existing `seedance_video.py` test script (which proves the AIHubMix API pattern works end-to-end) and the open-source `seedance2-comfyui` reference project (which provides the ComfyUI node framework and tensor conversion patterns).

The API client should closely mirror the test script's `create_video` and `wait_for_video` functions, adapting them into a class-based module with proper error handling for ComfyUI consumption. ComfyUI nodes follow a strict class-based pattern with `INPUT_TYPES` (classmethod), `RETURN_TYPES`, `FUNCTION`, `CATEGORY`, and a main execution method. All synchronous -- no async needed since ComfyUI executes nodes serially per prompt.

**Primary recommendation:** Fork the reference project's node structure and adapt the API layer from the test script. Use a single `api_client.py` module for all AIHubMix communication, a separate `nodes.py` for ComfyUI node definitions, and `__init__.py` for registration.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** T2V node outputs `video_url` (STRING) and `video_id` (STRING) only. No first_frame extraction in Phase 1.
- **D-02:** `first_frame` (IMAGE) output is deferred to Phase 2 Save Video node, which will handle video download and frame extraction.
- **D-03:** API polling progress is shown via print/console logging to ComfyUI log window. No ComfyUI Web UI progress bar integration in Phase 1.
- **D-04:** Follow the test script pattern -- periodic status updates with progress percentage printed to console.
- **D-05:** API Key node is a simple string passthrough -- accepts STRING input and returns it as output for wiring to generation nodes.
- **D-06:** T2V node has an optional `api_key` field as fallback when not wired from the API Key node.
- **D-07:** No key format validation or masking -- keep it simple for v1.
- **D-08:** Error messages include both the API error and actionable suggestions (Chinese language with technical details for debugging).
- **D-09:** Use Python exceptions (raise) to surface errors in ComfyUI -- this is the standard ComfyUI error mechanism.

### Claude's Discretion
- File/module structure and naming conventions
- API client implementation details (class vs functions, retry logic, timeout values)
- SIZE_MAP data structure (reuse from test script)
- Node parameter definitions (INT vs FLOAT for duration, enum choices for resolution/ratio)
- Polling interval (5 seconds per test script)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PFND-01 | Plugin registers with ComfyUI via `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS` in `__init__.py` | Reference project `__init__.py` pattern; ComfyUI official walkthrough |
| PFND-02 | All nodes appear under "Seedance 2.0" category in ComfyUI node menu | `CATEGORY = "Seedance 2.0"` on each node class |
| PFND-03 | `requirements.txt` lists all dependencies (requests, opencv-python, Pillow) | Reference project requirements.txt; CLAUDE.md stack section |
| APIC-01 | API client module handles all AIHubMix HTTP communication | Test script `seedance_video.py` provides proven patterns; API endpoints documented |
| APIC-02 | Authentication uses `Authorization: Bearer {key}` header | Test script line 73 confirms pattern; AIHubMix docs confirm |
| APIC-03 | API client polls for video completion every 5 seconds with progress logging to console | Test script `wait_for_video` function; CONTEXT.md D-03/D-04 locked |
| APIC-04 | Error handling provides clear messages for 401/402/429/network failures | CONTEXT.md D-08/D-09 locked; reference project `_check` function pattern |
| APIC-05 | Model identifier `doubao-seedance-2-0-260128` is used for all requests | Test script line 12; AIHubMix docs |
| KEYM-01 | Dedicated API Key node accepts STRING input and passes to generation nodes | CONTEXT.md D-05 locked; reference project `Seedance2ApiKey` class |
| KEYM-02 | Each generation node has optional `api_key` field as fallback | CONTEXT.md D-06 locked; reference project pattern |
| KEYM-03 | Missing API key produces clear error message with instructions | Simple guard clause in node `run()` method |
| T2V-01 | User provides text prompt to generate video via AIHubMix T2V | Test script `create_video` function; API POST `/v1/videos` |
| T2V-02 | User can select resolution and aspect ratio | Test script `SIZE_MAP` and `get_size` function |
| T2V-03 | User can set video duration (4-15 seconds, default 5) | Test script `--duration` argument pattern |
| T2V-04 | Node outputs video_url (STRING), video_id (STRING) | CONTEXT.md D-01 overrides REQUIREMENTS.md T2V-04 (no first_frame in Phase 1) |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | >= 3.8 | Runtime | ComfyUI minimum. 3.10+ allows `str \| None` type hints. Verified: 3.10.11 on dev machine. |
| requests | >= 2.28 | HTTP client for all AIHubMix communication | Synchronous-only is correct (ComfyUI blocks on node execution). Proven in test script. Standard in ComfyUI ecosystem. |
| PyTorch | >= 2.0 | Tensor handling (IMAGE format) | Already installed with ComfyUI. Do NOT install separately. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| opencv-python | >= 4.7 | Video frame extraction | Phase 2 (Save Video node). Not needed in Phase 1. |
| Pillow (PIL) | >= 9.0 | Tensor-to-image for API upload | Phase 2 (I2V base64 encoding). Not needed in Phase 1 T2V. |
| numpy | >= 1.23 | Array dtype conversion | Already with PyTorch. Used for float32->uint8 conversion in Phase 2. |

### Phase 1 Only Dependencies
| Library | Version | Purpose |
|---------|---------|---------|
| requests | >= 2.28 | All API communication (create, poll) |

**Phase 1 `requirements.txt`:**
```
requests>=2.28.0
```
Note: opencv-python, Pillow, numpy, torch are already present in any ComfyUI installation. Including them in requirements.txt is optional but common practice (reference project includes them for completeness). Recommendation: include all for safety, matching the reference project.

**Full `requirements.txt` (recommended):**
```
requests>=2.28.0
Pillow>=9.0.0
numpy>=1.23.0
opencv-python>=4.7.0
```
Do NOT include `torch` -- ComfyUI manages its own PyTorch installation and version pinning.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| requests (sync) | httpx (sync+async) | httpx adds async capability but ComfyUI is synchronous. No benefit, extra dependency. |
| requests (sync) | aiohttp (async-only) | Requires event loop. Conflicts with ComfyUI's sync execution model. |
| manual polling loop | tenacity/backoff | Over-engineered for a single create-poll flow. Test script proves manual loop works. |

**Version verification:** Package versions come from CLAUDE.md (pre-verified against PyPI) and the reference project's `requirements.txt`. The packages are stable, widely-used libraries with infrequent breaking changes. Confirmed HIGH confidence.

## Architecture Patterns

### Recommended Project Structure
```
seedance_comfyui/                   # ComfyUI custom_nodes/ subdirectory
├── __init__.py                     # NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
├── nodes.py                        # ComfyUI node classes (SeedanceApiKey, SeedanceTextToVideo)
├── api_client.py                   # AIHubMix API client (create, poll, error handling)
├── requirements.txt                # pip dependencies
└── README.md                       # Installation instructions (Phase 4)
```

### Pattern 1: ComfyUI Node Class Structure
**What:** Every ComfyUI node is a Python class with specific class-level attributes and methods.
**When to use:** For every node (API Key, T2V, future I2V/Extend/Omni nodes).

```python
# Source: ComfyUI official walkthrough + reference project
class SeedanceTextToVideo:
    # Required: node category in ComfyUI menu
    CATEGORY = "Seedance 2.0"

    # Required: ComfyUI calls this to discover inputs
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "duration": ("INT", {"default": 5, "min": 4, "max": 15}),
                "resolution": (["1080p", "720p", "480p"], {"default": "1080p"}),
                "ratio": (["16:9", "9:16", "4:3", "3:4", "1:1", "21:9"], {"default": "16:9"}),
            }
        }

    # Required: output types tuple
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "video_id")

    # Required: name of the main execution method
    FUNCTION = "generate"

    # Required: is this an output node? (No for T2V)
    OUTPUT_NODE = False

    def generate(self, prompt, api_key="", duration=5, resolution="1080p", ratio="16:9"):
        # Validate API key
        if not api_key:
            raise ValueError(
                "API key is required. "
                "Please connect an API Key node or fill in the api_key field. "
                "You can get your key at aihubmix.com"
            )

        # Call API client to create and poll for video
        result = create_and_wait(api_key, prompt, duration, resolution, ratio)
        return (result["video_url"], result["video_id"])
```

### Pattern 2: Plugin Registration (__init__.py)
**What:** ComfyUI scans `custom_nodes/*/` for `__init__.py` files that export mappings.
**When to use:** Once, in the plugin root.

```python
# Source: Reference project __init__.py
from .nodes import (
    SeedanceApiKey,
    SeedanceTextToVideo,
)

NODE_CLASS_MAPPINGS = {
    "SeedanceApiKey": SeedanceApiKey,
    "SeedanceTextToVideo": SeedanceTextToVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceApiKey": "Seedance 2.0 API Key",
    "SeedanceTextToVideo": "Seedance 2.0 Text to Video",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
```

### Pattern 3: API Client Module
**What:** Separate module encapsulating all AIHubMix HTTP communication.
**When to use:** All API calls go through this module. Nodes should never call `requests` directly.

```python
# Source: Test script seedance_video.py patterns
import requests
import time

BASE_URL = "https://aihubmix.com/v1"
MODEL = "doubao-seedance-2-0-260128"

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
}

def _get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

def _get_size(resolution, ratio):
    """Return size string, or None for 1080p (API default)."""
    if resolution == "1080p":
        return None
    return SIZE_MAP.get((resolution, ratio))

def create_video(api_key, prompt, duration=5, resolution="1080p", ratio="16:9"):
    headers = _get_headers(api_key)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "seconds": duration,
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

def wait_for_video(api_key, video_id, poll_interval=5, max_wait=600):
    headers = _get_headers(api_key)
    status = "queued"
    progress = 0
    elapsed = 0

    while status in ("in_progress", "queued") and elapsed < max_wait:
        try:
            resp = requests.get(f"{BASE_URL}/videos/{video_id}", headers=headers)
            if resp.status_code != 200:
                print(f"[Seedance] Status check error ({resp.status_code}), retrying...")
                time.sleep(poll_interval)
                elapsed += poll_interval
                continue

            data = resp.json()
            status = data.get("status", status)
            progress = data.get("progress", progress) or 0
            print(f"[Seedance] {status} - {progress}%")
        except requests.RequestException as e:
            print(f"[Seedance] Network error: {e}, retrying...")

        time.sleep(poll_interval)
        elapsed += poll_interval

    if status == "failed":
        error_msg = "Unknown error"
        error_data = data.get("error")
        if isinstance(error_data, dict):
            error_msg = error_data.get("message", error_msg)
        elif isinstance(error_data, str):
            error_msg = error_data
        raise RuntimeError(f"Video generation failed: {error_msg}")

    if status != "completed":
        raise RuntimeError(f"Video generation timed out after {max_wait}s (status: {status})")

    return data

def _check_response(resp):
    """Raise descriptive errors for common API failures."""
    if resp.status_code == 200:
        return
    if resp.status_code == 401:
        raise RuntimeError(
            "Authentication failed (401): Please check your API key is correct. "
            "You can view your key at aihubmix.com"
        )
    if resp.status_code == 402:
        raise RuntimeError(
            "Insufficient balance (402): Please top up at aihubmix.com"
        )
    if resp.status_code == 429:
        raise RuntimeError(
            "Rate limited (429): Too many requests. Please wait and try again."
        )
    resp.raise_for_status()
```

### Pattern 4: API Key Passthrough Node
**What:** A node that simply passes a string through for wiring.
**When to use:** When you want users to enter their API key once and wire it to multiple generation nodes.

```python
# Source: Reference project Seedance2ApiKey class
class SeedanceApiKey:
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
```

### Anti-Patterns to Avoid
- **Async in nodes:** ComfyUI execution engine is synchronous. Never use `asyncio`, `async/await`, or `aiohttp` in node methods. Verified: ComfyUI official docs and reference project both use synchronous patterns.
- **Hardcoded API keys:** Never embed test/development API keys in source code. The test script has one for CLI testing but plugin code must never include it.
- **Global mutable state:** Do not store API keys or video state in module-level variables. ComfyUI can execute multiple prompts concurrently in separate threads. Pass all data through method parameters.
- **Printing to sys.stdout with carriage return:** The test script uses `\r` for progress bar updates. In ComfyUI, use plain `print()` statements instead -- ComfyUI captures stdout and displays in its log pane.
- **sys.exit() in plugin code:** The test script uses `sys.exit()` for errors. In ComfyUI nodes, use `raise RuntimeError()` or `raise ValueError()` instead. `sys.exit()` kills the entire ComfyUI process.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Resolution/ratio mapping | Custom mapping logic | Test script SIZE_MAP | All valid combos already enumerated. Missing combos (1080p + ratio) are intentional (API default). |
| Video ID extraction | Custom response parsing | `data.get("id") or data.get("video_id")` | Test script already handles both possible response keys. |
| HTTP error handling | Generic try/except | Status-code-specific messages | CONTEXT.md D-08 requires specific messages per error type (401/402/429/network). |
| ComfyUI tensor conversion | Custom numpy/torch code | Standard patterns from reference project | Phase 2 will need this (I2V). Phase 1 T2V does not produce IMAGE output. |

**Key insight:** The test script `seedance_video.py` is a proven, working implementation of the entire API interaction. The API client module should be a clean adaptation of it, not a rewrite. The primary changes are: (1) remove `sys.exit()` calls, (2) replace with `raise RuntimeError()`, (3) add Chinese error messages per D-08, (4) wrap in functions instead of a CLI script.

## Common Pitfalls

### Pitfall 1: Wrong Node Output Type for T2V-04 Override
**What goes wrong:** REQUIREMENTS.md says T2V-04 outputs `(STRING, IMAGE, STRING)` but CONTEXT.md D-01 overrides to `(STRING, STRING)` only (no first_frame). Using the wrong tuple causes ComfyUI to crash with a tuple length mismatch.
**Why it happens:** REQUIREMENTS.md was written before the context discussion refined the scope.
**How to avoid:** Use `RETURN_TYPES = ("STRING", "STRING")` and `RETURN_NAMES = ("video_url", "video_id")`. No IMAGE output in Phase 1.
**Warning signs:** ComfyUI error "expected N return values, got M" at runtime.

### Pitfall 2: API Key Not Provided via Wire
**What goes wrong:** User forgets to wire the API Key node to the T2V node, and the optional `api_key` field is empty. The API call fails with 401 but the error message is unhelpful.
**Why it happens:** ComfyUI optional inputs default to their specified default value (empty string for STRING).
**How to avoid:** Check `if not api_key` at the start of the T2V `generate()` method and raise a clear error with instructions. Per KEYM-03.
**Warning signs:** Generic 401 errors instead of actionable messages.

### Pitfall 3: Missing Resolution/Ratio Combination
**What goes wrong:** User selects `("1080p", "21:9")` or `("480p", "3:4")` and it's not in SIZE_MAP.
**Why it happens:** The API only supports specific resolution/ratio combinations.
**How to avoid:** For 1080p, always return None (API default, all ratios supported). For 480p/720p, only offer ratios that exist in SIZE_MAP. Use ComfyUI's enum/list input type to constrain choices at the UI level.
**Warning signs:** API returns 400 error with "invalid size" message.

### Pitfall 4: Polling Blocks ComfyUI Indefinitely
**What goes wrong:** Video generation takes 1-5 minutes. During polling, the ComfyUI UI appears frozen because the node's `run()` method is blocked.
**Why it happens:** ComfyUI executes nodes synchronously. Long API waits are inherent to video generation.
**How to avoid:** Implement a `max_wait` timeout (600 seconds / 10 minutes is generous). Print periodic progress updates so the user sees activity in the log. This is expected behavior for video generation nodes in ComfyUI.
**Warning signs:** User reports "ComfyUI crashed" when it's actually just waiting for the API.

### Pitfall 5: Forgetting `OUTPUT_NODE = False`
**What goes wrong:** Setting `OUTPUT_NODE = True` on a T2V node causes ComfyUI to treat it as a terminal node, potentially affecting execution order.
**Why it happens:** Copy-paste from examples or misunderstanding which nodes need `OUTPUT_NODE = True` (only Save/Preview nodes).
**How to avoid:** T2V is an intermediate node (`OUTPUT_NODE = False`). Only the Save Video node (Phase 2) is an output node.
**Warning signs:** Workflow execution order issues, or nodes not executing when expected.

### Pitfall 6: Incorrect AUTH Header for AIHubMix
**What goes wrong:** Using `x-api-key` header (muapi.ai pattern from reference project) instead of `Authorization: Bearer` (AIHubMix pattern).
**Why it happens:** The reference project uses muapi.ai which has different authentication. Forking without changing the auth header produces 401 errors.
**How to avoid:** Use `Authorization: Bearer {api_key}` header. This is confirmed in the test script (line 73) and AIHubMix docs.
**Warning signs:** 401 errors even with a valid API key.

## Code Examples

### Complete API Client Pattern (create + poll combined)
```python
# Source: Adapted from seedance_video.py test script
# This is the core function that T2V node's generate() method calls

def create_and_wait(api_key, prompt, duration=5, resolution="1080p", ratio="16:9"):
    """Create a video and wait for completion. Returns result dict."""
    # Step 1: Create
    video_id = create_video(api_key, prompt, duration, resolution, ratio)
    print(f"[Seedance] Video created: {video_id}")

    # Step 2: Poll
    result = wait_for_video(api_key, video_id)
    print(f"[Seedance] Video completed: {result.get('video_url', 'N/A')}")

    # Step 3: Return outputs
    video_url = result.get("video_url") or result.get("url", "")
    return {
        "video_url": video_url,
        "video_id": video_id,
    }
```

### ComfyUI `__init__.py` Registration
```python
# Source: Reference project pattern (confirmed working)
from .nodes import SeedanceApiKey, SeedanceTextToVideo

NODE_CLASS_MAPPINGS = {
    "SeedanceApiKey": SeedanceApiKey,
    "SeedanceTextToVideo": SeedanceTextToVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceApiKey": "Seedance 2.0 API Key",
    "SeedanceTextToVideo": "Seedance 2.0 Text to Video",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
```

### Input Type Definitions for T2V Node
```python
# Source: Reference project pattern + test script CLI args
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
```

### Error Messages with Chinese User-Facing Text
```python
# Source: CONTEXT.md D-08 locked decision

ERROR_MESSAGES = {
    401: "Authentication failed (401): Please check your API key. View it at aihubmix.com",
    402: "Insufficient balance (402): Please top up at aihubmix.com",
    429: "Rate limited (429): Too many requests. Please wait and retry.",
    "network": "Network error: Please check your network connection.",
    "no_key": "API key is required. Connect an API Key node or fill in the api_key field. Get your key at aihubmix.com",
    "no_video_id": "No video ID returned from API. Response: {data}",
    "failed": "Video generation failed: {error}",
    "timeout": "Video generation timed out after {max_wait}s (status: {status})",
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| muapi.ai API (`x-api-key` header, `/api/v1/` prefix) | AIHubMix API (`Authorization: Bearer`, `/v1/` prefix) | Project decision | Different auth header, different endpoint prefix, OpenAI-compatible format |
| Reference project single-file nodes | Separate api_client.py + nodes.py | This project | Cleaner separation of concerns; API logic testable independently |
| sys.exit() for errors (CLI script) | raise RuntimeError() (ComfyUI node) | This project | ComfyUI catches exceptions and displays in UI; sys.exit kills the process |

**Deprecated/outdated:**
- muapi.ai-specific patterns from reference project (auth header, endpoint URLs, response field names) must not be copied blindly. Only the ComfyUI node structure patterns are reusable.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime | Yes | 3.10.11 | -- |
| git | Version control, ComfyUI Manager install | Yes | 2.45.1 | -- |
| requests | API client (Phase 1 core) | Not on dev machine | -- | Installed via requirements.txt in ComfyUI environment |
| PyTorch | IMAGE tensor support | Not on dev machine | -- | Pre-installed with ComfyUI |
| opencv-python | Frame extraction | Not on dev machine | -- | Phase 2 only; installed via requirements.txt |
| Pillow | Image encoding | Not on dev machine | -- | Phase 2 only; installed via requirements.txt |
| ComfyUI | Plugin host | Not on dev machine | -- | Target runtime environment |

**Missing dependencies with no fallback:**
- None blocking Phase 1 development. The development machine does not need ComfyUI or the Python packages installed -- code can be written and tested against the API independently using the test script pattern.

**Missing dependencies with fallback:**
- requests/PyTorch/etc. not installed on dev machine: Expected. These are needed only in the ComfyUI runtime environment. Development can proceed with API testing via the existing `seedance_video.py` test script.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (recommended) |
| Config file | None -- see Wave 0 |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PFND-01 | NODE_CLASS_MAPPINGS exported from __init__.py | unit | `pytest tests/test_registration.py::test_node_class_mappings -x` | Wave 0 |
| PFND-02 | All nodes have CATEGORY = "Seedance 2.0" | unit | `pytest tests/test_registration.py::test_node_categories -x` | Wave 0 |
| PFND-03 | requirements.txt lists correct dependencies | unit | `pytest tests/test_registration.py::test_requirements -x` | Wave 0 |
| APIC-01 | API client creates, polls, handles responses | unit (mocked) | `pytest tests/test_api_client.py -x` | Wave 0 |
| APIC-02 | Auth header is `Authorization: Bearer {key}` | unit (mocked) | `pytest tests/test_api_client.py::test_auth_header -x` | Wave 0 |
| APIC-03 | Polling loops with progress logging | unit (mocked) | `pytest tests/test_api_client.py::test_polling -x` | Wave 0 |
| APIC-04 | Error messages for 401/402/429/network | unit (mocked) | `pytest tests/test_api_client.py::test_error_handling -x` | Wave 0 |
| APIC-05 | Model ID is `doubao-seedance-2-0-260128` | unit | `pytest tests/test_api_client.py::test_model_id -x` | Wave 0 |
| KEYM-01 | API Key node passes string through | unit | `pytest tests/test_nodes.py::test_api_key_passthrough -x` | Wave 0 |
| KEYM-02 | T2V has optional api_key field | unit | `pytest tests/test_nodes.py::test_t2v_optional_key -x` | Wave 0 |
| KEYM-03 | Missing key raises clear error | unit | `pytest tests/test_nodes.py::test_missing_key_error -x` | Wave 0 |
| T2V-01 | T2V sends prompt to API | unit (mocked) | `pytest tests/test_nodes.py::test_t2v_prompt -x` | Wave 0 |
| T2V-02 | T2V supports resolution/ratio selection | unit | `pytest tests/test_nodes.py::test_t2v_size_options -x` | Wave 0 |
| T2V-03 | T2V duration 4-15 with default 5 | unit | `pytest tests/test_nodes.py::test_t2v_duration -x` | Wave 0 |
| T2V-04 | T2V outputs (video_url, video_id) only | unit (mocked) | `pytest tests/test_nodes.py::test_t2v_outputs -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green, plus manual integration test with ComfyUI

### Wave 0 Gaps
- [ ] `tests/test_registration.py` -- covers PFND-01, PFND-02, PFND-03
- [ ] `tests/test_api_client.py` -- covers APIC-01 through APIC-05
- [ ] `tests/test_nodes.py` -- covers KEYM-01 through KEYM-03, T2V-01 through T2V-04
- [ ] `tests/conftest.py` -- shared fixtures (mock API responses, sample video data)
- [ ] `pytest` install: `pip install pytest pytest-mock` -- if not present in environment

## Sources

### Primary (HIGH confidence)
- `seedance_video.py` test script -- Complete AIHubMix API interaction pattern, proven working. SIZE_MAP, create/poll/download, error handling.
- ComfyUI Official Docs - Custom Node Walkthrough (https://docs.comfy.org/custom-nodes/walkthrough) -- NODE_CLASS_MAPPINGS registration, node class structure, INPUT_TYPES pattern.
- ComfyUI Official Docs - Tensors (https://docs.comfy.org/custom-nodes/backend/tensors) -- IMAGE format [B,H,W,C] float32.
- Reference Project: Anil-matcha/seedance2-comfyui (https://github.com/Anil-matcha/seedance2-comfyui) -- Node structure, registration, API key passthrough pattern, requirements.txt.
- AIHubMix API Docs (https://docs.aihubmix.com/en/api/Video-Gen) -- Endpoint specifications, request/response format.

### Secondary (MEDIUM confidence)
- AIHubMix Chinese docs (https://docs.aihubmix.com/zh-CN/api/Video-Gen) -- Additional details on polling interval (15s recommended but 5s works), typical generation time (1-5 minutes).
- ComfyUI ecosystem patterns -- Multiple custom node repos confirm synchronous execution model and requests library usage.

### Tertiary (LOW confidence)
- Model listing visibility on AIHubMix docs page -- Seedance model not prominently listed in visible model table, but test script confirms `doubao-seedance-2-0-260128` works. The model may be available but not in the default visible list.

## Open Questions

1. **AIHubMix completed response format for video_url**
   - What we know: Test script uses `result.get("video_url")` but the field name might vary. The API returns a completed status with video data.
   - What's unclear: Exact field name in completed response (could be `video_url`, `url`, `content_url`, or nested under `output`).
   - Recommendation: Use defensive parsing: `result.get("video_url") or result.get("url", "")` as shown in the code example. Adjust during integration testing.

2. **ComfyUI Manager compatibility for "Install via Git URL"**
   - What we know: ComfyUI Manager supports installing custom nodes from Git URLs. The plugin needs `__init__.py` with `NODE_CLASS_MAPPINGS` at root.
   - What's unclear: Whether any additional metadata files are needed for ComfyUI Manager to recognize the plugin.
   - Recommendation: Follow the reference project structure exactly. PFND-04 (ComfyUI Manager install) is Phase 4 scope, so this can be validated then.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- All libraries are stable, well-known, proven in both the test script and reference project.
- Architecture: HIGH -- ComfyUI node patterns are well-documented and confirmed by both official docs and reference project.
- Pitfalls: HIGH -- Derived from direct comparison of test script vs reference project vs ComfyUI docs. Key differences (auth header, sys.exit vs raise) are documented.

**Research date:** 2026-04-03
**Valid until:** 2026-05-03 (stable domain, low churn expected)

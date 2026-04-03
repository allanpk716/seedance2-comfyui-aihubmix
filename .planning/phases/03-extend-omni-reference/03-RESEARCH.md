# Phase 3: Extend + Omni Reference - Research

**Researched:** 2026-04-03
**Domain:** AIHubMix Video API (Seedance 2.0), ComfyUI Custom Nodes
**Confidence:** MEDIUM (API payload formats unverified per D-14)

## Summary

Phase 3 adds two new ComfyUI nodes to the Seedance 2.0 plugin: **Video Extend** (continue a previously generated video using its video_id) and **Omni Reference** (combine up to 9 images + 3 video URLs + a text prompt for multi-modal generation). Both must work through the AIHubMix API.

The critical challenge is that AIHubMix's published Video Generation API documentation only covers basic text-to-video and image-to-video generation for veo, sora, and wan models. It does NOT document Seedance-specific extend or omni reference operations. The existing plugin already works for T2V and I2V using the model ID `doubao-seedance-2-0-260128` with `POST /v1/videos`, which proves AIHubMix routes Seedance requests through this unified endpoint. However, the exact payload fields for extend (likely referencing a prior video_id) and omni (likely passing arrays of images/videos) are unknown and must be empirically verified via the test script before node implementation begins (D-14).

The OpenAI video API spec provides a strong hint: `POST /v1/videos/extensions` with `{"video": {"id": "video_123"}, "prompt": "...", "seconds": "4"}` is the standard extend format. Since AIHubMix claims OpenAI compatibility, this endpoint may work. For omni reference, the MuAPI reference project uses `images_list`, `video_files`, and `@image1`/`@video1` placeholder syntax in prompts.

**Primary recommendation:** Follow D-14 strictly -- extend `seedance_video.py` to test both extend and omni payload hypotheses against the real API BEFORE writing any node code. Plan two waves: Wave 1 for API verification, Wave 2 for node implementation (only if verification succeeds).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-14:** API verification priority -- test Extend/Omni payload formats via `seedance_video.py` before building nodes. Unavailable features move out of this phase.
- **D-15:** Extend/Omni nodes use existing output format `(video_url: STRING, video_id: STRING)`, consistent with T2V/I2V. first_frame (IMAGE) output not implemented, consistent with D-01/D-10/D-11.
- **D-16:** Omni Reference uses fixed slots -- 9 optional IMAGE inputs + 3 optional STRING inputs (video URLs). Unconnected slots auto-ignored. Uses ComfyUI optional input blocks like I2V's `api_key` pattern.
- **D-17:** Omni prompt format (whether @image1/@video1 placeholders are needed) confirmed during API verification. Start with MuAPI placeholder format as hypothesis.

### Claude's Discretion
- Extend node parameter layout (video_id input + optional prompt + generation parameters)
- Omni node 9+3 input naming (image_1..image_9, video_url_1..video_url_3)
- API client new function naming (create_extend_video / create_omni_video etc.)
- API verification test script specific implementation
- Error message wording (follow D-08 Chinese style)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EXTD-01 | User provides video_id from prior generation + optional continuation prompt | OpenAI video extend API uses `{"video": {"id": "video_id"}}` format; MuAPI uses `request_id` field. API verification needed to confirm which format AIHubMix accepts. |
| EXTD-02 | Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING) | Per D-15: first_frame not implemented. Output is `(STRING, STRING)` only. |
| EXTD-03 | User can select resolution, aspect ratio, duration same as T2V | Reuse existing SIZE_MAP and _get_size() helper. Same parameter pattern as T2V/I2V. |
| OMNI-01 | User can combine multiple images (up to 9) + video URLs (up to 3) + prompt | Per D-16: 9 optional IMAGE + 3 optional STRING inputs. MuAPI reference uses `images_list`/`video_files` arrays. API verification needed. |
| OMNI-02 | Each image input converted from ComfyUI tensor to base64 data URI | Reuse exact pattern from SeedanceImageToVideo (lines 128-133 in nodes.py). Loop over all connected images. |
| OMNI-03 | Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING) | Per D-15: first_frame not implemented. Output is `(STRING, STRING)` only. |
</phase_requirements>

## Standard Stack

### Core (unchanged from Phase 1/2)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | >= 3.10 | Runtime | ComfyUI minimum, already in use |
| requests | >= 2.28 | HTTP client for AIHubMix API | Synchronous, proven in T2V/I2V |
| opencv-python | >= 4.7 | Video frame extraction (Save Video only) | Already in requirements.txt |
| Pillow | >= 9.0 | IMAGE tensor to JPEG conversion for API upload | Reused from I2V pattern |
| numpy | >= 1.23 | Array manipulation | Already with PyTorch |
| pytest | >= 7.0 | Testing framework | Already configured, conftest.py exists |

### No new dependencies needed
Phase 3 reuses all existing dependencies. No new packages required.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Fixed 9+3 input slots | Dynamic input list | Dynamic inputs require custom ComfyUI JS widgets, far more complex. Fixed slots with optional inputs are the ComfyUI convention for variable-count inputs. |

## Architecture Patterns

### Recommended Project Structure (no changes)
```
seedance_comfyui/
  __init__.py          # Add SeedanceExtendVideo, SeedanceOmniReference to mappings
  api_client.py        # Add create_extend_video, create_omni_video functions
  nodes.py             # Add SeedanceExtendVideo, SeedanceOmniReference classes
  seedance_video.py    # Extend with --extend and --omni test subcommands
  tests/
    conftest.py        # Add fixtures for extend/omni test data
    test_api_client.py # Add TestCreateExtendVideo, TestCreateOmniVideo classes
    test_nodes.py      # Add TestSeedanceExtendVideo, TestSeedanceOmniReference classes
```

### Pattern 1: API Client Functions (extend existing pattern)
**What:** Function-based API client (not class-based) with `create_*` and `create_and_wait_*` pairs.
**When to use:** All API-facing operations.
**Example:**
```python
# Source: Existing api_client.py pattern
def create_extend_video(api_key, video_id, prompt="", duration=5, resolution="1080p", ratio="16:9"):
    """Submit a video extend task. Returns video ID string."""
    headers = _get_headers(api_key)
    payload = {
        "model": MODEL,
        # Payload fields TBD based on API verification
        # Hypothesis A (OpenAI format): {"video": {"id": video_id}, "prompt": prompt, "seconds": duration}
        # Hypothesis B (MuAPI format): {"request_id": video_id, "prompt": prompt, "duration": duration}
    }
    size = _get_size(resolution, ratio)
    if size:
        payload["size"] = size
    resp = requests.post(f"{BASE_URL}/videos", headers=headers, json=payload)
    _check_response(resp)
    data = resp.json()
    return data.get("id") or data.get("video_id")

def create_and_wait_extend(api_key, video_id, prompt="", duration=5, resolution="1080p", ratio="16:9"):
    """Create extend video and wait for completion. Returns result dict."""
    new_id = create_extend_video(api_key, video_id, prompt, duration, resolution, ratio)
    result = wait_for_video(api_key, new_id)
    video_url = result.get("video_url") or result.get("url", "")
    return {"video_url": video_url, "video_id": new_id}
```

### Pattern 2: ComfyUI Node with Many Optional Inputs (Omni)
**What:** ComfyUI INPUT_TYPES with large optional block for variable-count inputs.
**When to use:** Omni Reference node with 9 IMAGE + 3 STRING optional inputs.
**Example:**
```python
# Source: ComfyUI custom node API convention, adapted from SeedanceImageToVideo
class SeedanceOmniReference:
    CATEGORY = "Seedance 2.0"

    @classmethod
    def INPUT_TYPES(cls):
        optional = {
            "api_key": ("STRING", {"default": ""}),
            "duration": ("INT", {"default": 5, "min": 4, "max": 15, "step": 1}),
            "resolution": (["1080p", "720p", "480p"],),
            "ratio": (["16:9", "9:16", "4:3", "3:4", "1:1", "21:9"],),
        }
        # Add 9 optional IMAGE inputs
        for i in range(1, 10):
            optional[f"image_{i}"] = ("IMAGE",)
        # Add 3 optional STRING inputs for video URLs
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
```

### Pattern 3: Multi-Image Tensor to Base64 Conversion Loop
**What:** Convert multiple ComfyUI IMAGE tensors to base64 data URIs, skipping None/unconnected.
**When to use:** Omni Reference node's generate() method.
**Example:**
```python
# Source: Adapted from SeedanceImageToVideo.generate() in nodes.py lines 128-133
def _tensor_to_data_uri(tensor):
    """Convert single ComfyUI IMAGE tensor to JPEG base64 data URI."""
    image_array = np.clip(tensor[0].cpu().numpy() * 255, 0, 255).astype(np.uint8)
    pil_image = Image.fromarray(image_array)
    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG", quality=95)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

# In generate() method:
image_data_uris = []
for i in range(1, 10):
    img = locals().get(f"image_{i}")
    if img is not None:
        image_data_uris.append(_tensor_to_data_uri(img))
```

### Anti-Patterns to Avoid
- **Do NOT build Omni node with a single "images" input accepting a batch tensor.** ComfyUI workflows need individual slots for wiring different image sources. Batch tensors cannot represent "these images came from different nodes."
- **Do NOT hardcode the extend/omni payload format before API verification.** The payload is unverified. Build with a hypothesis but validate first.
- **Do NOT create a separate api_client_extend.py or similar module.** Keep all API functions in the single api_client.py per Phase 1 decision.
- **Do NOT share video_id as an integer.** It must be a STRING type in ComfyUI because it flows between nodes via STRING connections.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Image tensor to base64 conversion | Custom encoding logic per image | Existing I2V pattern (nodes.py lines 128-133) | Already tested, handles edge cases (clipping, dtype) |
| API response error handling | New error handling for extend/omni | Existing `_check_response()` and `_check_response` pattern | Covers 401/402/429 with Chinese messages per D-08 |
| Polling for video completion | New polling logic | Existing `wait_for_video()` | Proven, handles network errors, timeout, progress logging |
| Resolution/size mapping | New size logic | Existing `SIZE_MAP` and `_get_size()` | Covers all resolution/ratio combinations |

## Common Pitfalls

### Pitfall 1: AIHubMix Extend Endpoint May Not Exist
**What goes wrong:** AIHubMix may not support video extend at all for the Seedance model, even though the MuAPI reference project does.
**Why it happens:** AIHubMix is a third-party API aggregator. They may not have implemented all Seedance operations. Their docs only list veo, sora, and wan models.
**How to avoid:** D-14 mandates testing first. If extend returns 404 or an unsupported model error, mark extend as unavailable and remove it from this phase.
**Warning signs:** HTTP 404 on `/v1/videos/extensions`, or 400 with "unsupported operation" on `/v1/videos`.

### Pitfall 2: OpenAI vs MuAPI Payload Format Mismatch
**What goes wrong:** Implementing the MuAPI payload format (`request_id`, `images_list`) when AIHubMix actually expects the OpenAI format (`{"video": {"id": ...}}`).
**Why it happens:** The reference project (MuAPI) uses different field names and a different endpoint structure than the OpenAI-compatible format AIHubMix likely uses.
**How to avoid:** Test both formats during API verification. Start with the OpenAI format since AIHubMix advertises OpenAI compatibility. Fall back to MuAPI format if OpenAI format fails.
**Warning signs:** API returns 400 with validation error about unknown fields.

### Pitfall 3: Optional IMAGE Inputs Sending None
**What goes wrong:** ComfyUI passes `None` or raises errors when optional IMAGE inputs are not connected.
**Why it happens:** ComfyUI's handling of optional inputs varies by type. STRING optional inputs get default values, but IMAGE optional inputs may pass `None` or may not appear in kwargs at all.
**How to avoid:** Use `kwargs.get(f"image_{i}")` or `locals().get(f"image_{i}")` and check for `None` explicitly. Test with different numbers of connected inputs.
**Warning signs:** TypeError about missing required argument, or NoneType has no attribute errors.

### Pitfall 4: Omni Node Input Enum Becomes Unusable
**What goes wrong:** With 9+3+5 = 17 inputs, the Omni node becomes hard to use in the ComfyUI canvas.
**Why it happens:** ComfyUI renders all inputs vertically. 17 inputs create a very tall node.
**How to avoid:** This is acceptable per D-16 ("node will be large but intuitive"). Consider grouping: required (prompt), then generation params, then image_1..9, then video_url_1..3.
**Warning signs:** User complaints about node size -- but this is deferred to future UI improvements.

### Pitfall 5: Extend Video ID From Wrong Source
**What goes wrong:** Connecting a video URL instead of a video_id to the Extend node's input.
**Why it happens:** The Save Video node outputs both video_path and video_url, but the Extend node needs the raw video_id from the generation node.
**How to avoid:** The Extend node's video_id input should be wired directly from a generation node's video_id output (STRING), not from Save Video. Label the input clearly.
**Warning signs:** API returns 404 "video not found" because a URL was passed instead of an ID.

### Pitfall 6: Seedance 2.0 API Official Availability Status
**What goes wrong:** Building extend/omni features that depend on Seedance 2.0-specific capabilities when the model's official API may be limited.
**Why it happens:** As of March 2026, Volcengine's official docs say Seedance 2.0 does not yet support public API calls (experience center only). Third-party providers like AIHubMix may have special access but may also have gaps.
**How to avoid:** T2V and I2V already work with `doubao-seedance-2-0-260128`, proving AIHubMix has some Seedance 2.0 access. Verify extend/omni specifically. If they fail, remove from phase scope.
**Warning signs:** API returns model-specific errors, or extend/omni features silently produce lower-quality results than expected.

## Code Examples

### Existing Pattern: I2V API Function (model for extend/omni)
```python
# Source: api_client.py lines 138-175
def create_i2v_video(api_key, prompt, image_data_uri, duration=5, resolution="1080p", ratio="16:9"):
    headers = _get_headers(api_key)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "seconds": duration,
        "input": image_data_uri,
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
```

### Existing Pattern: Node with Optional API Key (model for extend/omni)
```python
# Source: nodes.py lines 90-136
class SeedanceImageToVideo:
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
```

### Test Pattern: Mock Patching in nodes.py namespace
```python
# Source: test_nodes.py line 147
# CRITICAL: Patch target must be "seedance_comfyui.nodes.create_and_wait"
# NOT "api_client.create_and_wait" because nodes.py imports into its own namespace

@patch("seedance_comfyui.nodes.create_and_wait_extend")
def test_extend_calls_api(self, mock_create_and_wait_extend):
    from seedance_comfyui.nodes import SeedanceExtendVideo
    mock_create_and_wait_extend.return_value = {
        "video_url": "https://example.com/extended.mp4",
        "video_id": "vid_ext_123",
    }
    node = SeedanceExtendVideo()
    result = node.generate(
        video_id="vid_original",
        prompt="continue the scene",
        api_key="key123",
    )
    assert result == ("https://example.com/extended.mp4", "vid_ext_123")
```

### __init__.py Update Pattern
```python
# Source: Current __init__.py, extended
from .nodes import (
    SeedanceApiKey, SeedanceTextToVideo, SeedanceImageToVideo,
    SeedanceSaveVideo,
    SeedanceExtendVideo,        # NEW
    SeedanceOmniReference,      # NEW
)

NODE_CLASS_MAPPINGS = {
    "SeedanceApiKey": SeedanceApiKey,
    "SeedanceTextToVideo": SeedanceTextToVideo,
    "SeedanceImageToVideo": SeedanceImageToVideo,
    "SeedanceSaveVideo": SeedanceSaveVideo,
    "SeedanceExtendVideo": SeedanceExtendVideo,            # NEW
    "SeedanceOmniReference": SeedanceOmniReference,        # NEW
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceApiKey": "Seedance 2.0 API Key",
    "SeedanceTextToVideo": "Seedance 2.0 Text to Video",
    "SeedanceImageToVideo": "Seedance 2.0 Image to Video",
    "SeedanceSaveVideo": "Seedance 2.0 Save Video",
    "SeedanceExtendVideo": "Seedance 2.0 Video Extend",          # NEW
    "SeedanceOmniReference": "Seedance 2.0 Omni Reference",      # NEW
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| MuAPI separate endpoints (`/api/v1/seedance-v2.0-extend`, `/api/v1/seedance-2.0-omni-reference`) | Unified `POST /v1/videos` (AIHubMix) or `POST /v1/videos/extensions` (OpenAI) | Pre-project | Payload format differs from reference project |
| MuAPI `x-api-key` auth | AIHubMix `Authorization: Bearer` auth | Pre-project | Headers already handled by _get_headers() |
| Volcengine Ark `CreateContentsGenerationsTasks` with `content` array | AIHubMix OpenAI-compatible `POST /v1/videos` with `model`/`prompt`/`seconds` | Pre-project | Simpler payload format at AIHubMix layer |

**Deprecated/outdated:**
- The reference project's endpoint-specific approach (different URLs for each operation) is NOT how AIHubMix works. AIHubMix uses a unified endpoint.
- The MuAPI `request_id` field name may not be what AIHubMix uses. OpenAI uses `{"video": {"id": ...}}` nested structure.

## Open Questions

1. **AIHubMix Extend payload format**
   - What we know: AIHubMix uses OpenAI-compatible format. OpenAI extend uses `POST /v1/videos/extensions` with `{"video": {"id": "video_id"}, "prompt": "...", "seconds": "4"}`. MuAPI uses `request_id` field.
   - What's unclear: Whether AIHubMix supports `/v1/videos/extensions` endpoint, or if extend goes through the standard `/v1/videos` endpoint with different payload fields.
   - Recommendation: Test both hypothesis A (OpenAI format with separate endpoint) and hypothesis B (unified endpoint with extend-specific fields). D-14 mandates this testing.

2. **AIHubMix Omni Reference payload format**
   - What we know: MuAPI uses `images_list`, `video_files`, `audio_files` arrays plus `@image1`/`@video1` placeholder syntax in prompts. OpenAI has no documented omni reference equivalent.
   - What's unclear: How AIHubMix accepts multiple images/videos for Seedance. Whether it uses arrays of data URIs, nested objects, or prompt placeholders.
   - Recommendation: Start with arrays of data URIs (matching I2V's single `input` field pattern extended to multiple). Test `@image1` placeholder syntax if arrays don't work.

3. **ComfyUI optional IMAGE input behavior**
   - What we know: STRING optional inputs get default values. I2V node uses optional STRING for api_key successfully.
   - What's unclear: Whether ComfyUI passes `None` for unconnected optional IMAGE inputs, or omits them from kwargs entirely.
   - Recommendation: Test during implementation with a minimal prototype. Use `kwargs.get()` pattern to safely handle both cases.

4. **Extend video_id source node**
   - What we know: Generation nodes output `(video_url, video_id)` as STRING. Save Video outputs `(frames, first_frame_path, video_path)`.
   - What's unclear: Whether users will intuitively understand they need to wire video_id from the generation node (not Save Video) to the Extend node.
   - Recommendation: Clear naming in INPUT_TYPES. Consider adding tooltip/default text.

## Environment Availability

Step 2.6: Environment audit for Phase 3.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime | Yes | 3.10.11 | -- |
| pytest | Testing | Yes | 9.0.2 | -- |
| requests | API client | Yes | (installed) | -- |
| opencv-python | Save Video (existing) | Yes | (installed) | -- |
| Pillow | Image conversion | Yes | (installed) | -- |
| torch | Tensor handling | Yes | (via ComfyUI) | -- |
| numpy | Array manipulation | Yes | (via ComfyUI) | -- |
| AIHubMix API | Video generation | Unknown | -- | No fallback -- if API doesn't support extend/omni, those features are descoped |
| Internet access | API calls | Yes | -- | -- |

**Missing dependencies with no fallback:**
- AIHubMix API support for Seedance extend/omni operations -- if the API does not support these, the corresponding features must be removed from this phase per D-14.

**Missing dependencies with fallback:**
- None. All local development dependencies are installed.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | None (default discovery in tests/ directory) |
| Quick run command | `python -m pytest tests/test_nodes.py tests/test_api_client.py -x -q` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EXTD-01 | Extend node accepts video_id STRING + optional prompt STRING | unit | `python -m pytest tests/test_nodes.py::TestSeedanceExtendVideo -x -q` | No -- Wave 0 |
| EXTD-01 | create_extend_video sends correct payload to API | unit | `python -m pytest tests/test_api_client.py::TestCreateExtendVideo -x -q` | No -- Wave 0 |
| EXTD-02 | Extend node returns (video_url: STRING, video_id: STRING) | unit | `python -m pytest tests/test_nodes.py::TestSeedanceExtendVideo::test_extend_return_types -x -q` | No -- Wave 0 |
| EXTD-03 | Extend node supports resolution/aspect ratio/duration params | unit | `python -m pytest tests/test_nodes.py::TestSeedanceExtendVideo::test_extend_size_options -x -q` | No -- Wave 0 |
| OMNI-01 | Omni node accepts 9 optional IMAGE + 3 optional STRING inputs | unit | `python -m pytest tests/test_nodes.py::TestSeedanceOmniReference::test_omni_input_types -x -q` | No -- Wave 0 |
| OMNI-01 | create_omni_video sends correct payload with multiple images | unit | `python -m pytest tests/test_api_client.py::TestCreateOmniVideo -x -q` | No -- Wave 0 |
| OMNI-02 | Omni node converts each IMAGE tensor to base64 data URI | unit | `python -m pytest tests/test_nodes.py::TestSeedanceOmniReference::test_omni_tensor_conversion -x -q` | No -- Wave 0 |
| OMNI-03 | Omni node returns (video_url: STRING, video_id: STRING) | unit | `python -m pytest tests/test_nodes.py::TestSeedanceOmniReference::test_omni_return_types -x -q` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_nodes.py tests/test_api_client.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_api_client.py` -- add TestCreateExtendVideo, TestCreateOmniVideo test classes
- [ ] `tests/test_nodes.py` -- add TestSeedanceExtendVideo, TestSeedanceOmniReference test classes
- [ ] `tests/conftest.py` -- add mock_extend_response, mock_omni_response fixtures
- [ ] API verification test in seedance_video.py -- extend test script with --extend and --omni modes

## Sources

### Primary (HIGH confidence)
- Existing codebase: `api_client.py`, `nodes.py`, `__init__.py`, `seedance_video.py` -- verified by reading source files
- ComfyUI Custom Node Walkthrough: https://docs.comfy.org/custom-nodes/walkthrough -- node structure patterns
- OpenAI Video Extend API: https://developers.openai.com/api/reference/resources/videos/methods/extend/ -- extend endpoint format

### Secondary (MEDIUM confidence)
- AIHubMix Video Generation API: https://docs.aihubmix.com/en/api/Video-Gen -- only documents veo/sora/wan models, no Seedance extend/omni
- Reference project (MuAPI): https://github.com/Anil-matcha/seedance2-comfyui -- payload format reference only, different API provider
- Volcengine Ark Seedance 2.0 API Reference: https://www.volcengine.com/docs/82379/1520757 -- official but JS-rendered, could not extract full content
- Volcengine Seedance 2.0 SDK Examples: https://www.volcengine.com/docs/82379/2291680 -- official but JS-rendered

### Tertiary (LOW confidence)
- LaoZhang AI Blog: https://blog.laozhang.ai/en/posts/seedance-2-api -- reports Seedance 2.0 official API not yet publicly available (March 2026); AIHubMix is a third-party aggregator that may have special access
- WebSearch results for AIHubMix extend/omni -- no direct documentation found for these operations
- MuAPI Omni node pattern with `@image1`/`@video1` placeholders -- unverified for AIHubMix

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies, all existing proven in Phase 1/2
- Architecture: HIGH -- follows established patterns from Phase 1/2 exactly
- Extend payload format: LOW -- no documentation found, must be verified empirically (D-14)
- Omni payload format: LOW -- no documentation found, must be verified empirically (D-14)
- Pitfalls: MEDIUM -- based on experience with similar APIs and the existing codebase

**Research date:** 2026-04-03
**Valid until:** 2026-04-30 (API availability may change -- re-verify if phase starts later)

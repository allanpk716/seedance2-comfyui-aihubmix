# Feature Landscape

**Domain:** ComfyUI custom node plugin for cloud-based AI video generation (Seedance 2.0 via AIHubMix API)
**Researched:** 2026-04-03
**Confidence:** HIGH (based on reference project source code, official docs, and ComfyUI ecosystem analysis)

---

## Table Stakes

Features users expect from any ComfyUI video generation plugin. Missing any of these means the product feels incomplete or broken.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Text-to-Video node** | Core value proposition. Every video gen plugin has this. | Low | Straightforward POST to `/v1/videos` with prompt, model, size, seconds. Reference project has proven pattern. |
| **Image-to-Video node** | Animating reference images is the second most common use case. Runway, Kling, Wan nodes all provide this. | Low | AIHubMix accepts image via `input` field (base64 data URI, URL, or file upload). No separate upload step needed unlike muapi.ai. |
| **API Key input node** | Users need a way to authenticate. Every API-based ComfyUI plugin has a dedicated API key node (Runway, Kling, Stability, etc.). | Low | Single STRING input node. Wire to all generation nodes. Falls back gracefully if blank (error message). |
| **API Key on each generation node** | Users who skip the dedicated key node still need to paste their key directly on the generation node. The `optional: api_key` field pattern is standard. | Low | Already in reference project. Set `default: ""` so it is optional. |
| **Resolution/size selector** | Users expect to choose output quality. The AIHubMix API supports `size` parameter with `480p`, `720p`, `1080p` variants. | Low | Use combo dropdown for resolution + aspect ratio. Map to size string via lookup table (already validated in `seedance_video.py`). |
| **Duration control** | Video length is a fundamental parameter. Users expect to set 4-15 seconds. | Low | INT input with min=4, max=15, default=5. |
| **Aspect ratio control** | Essential for different output formats (widescreen, portrait, square). | Low | Combo: 16:9, 9:16, 4:3, 3:4, 1:1, 21:9. Some combos not available at all resolutions -- see size map. |
| **Video download + save to disk** | Users must be able to save generated videos. The built-in ComfyUI `SaveVideo` node and custom saver nodes are standard. | Medium | Download via `GET /v1/videos/{id}/content`. Save to ComfyUI output directory. Return video file path. |
| **Video frames as IMAGE tensor** | Users need to pass video frames to downstream nodes (preview, upscale, VHS, etc.). The ComfyUI IMAGE type (B,H,W,C float32 tensor) is the standard interchange format. | Medium | Use OpenCV to extract frames from downloaded MP4. Return as torch tensor. Reference project has proven implementation in `seedance2_video_saver.py`. |
| **First frame output** | Users want a quick preview without loading all frames. First frame as IMAGE tensor is the reference project's standard output alongside video_url. | Low | Extract first frame with OpenCV. Return as (1,H,W,3) tensor. |
| **Video URL output** | Users need the CDN URL for sharing, external download, or re-use. All generation nodes output `video_url` as STRING. | Low | Return the URL from the API response. |
| **Request ID output** | Needed for video extend workflow. Every generation must output its request/video ID. | Low | Extract `id` or `video_id` from API response. |
| **Polling with progress feedback** | Video generation takes 30s-5min. Users need to see progress, not a frozen UI. Console logging with status updates is the minimum. | Medium | Poll `GET /v1/videos/{id}` every 5 seconds. Print status + progress % to console. AIHubMix returns `status` (queued/in_progress/completed/failed) and `progress` (0-100). |
| **Error handling with clear messages** | API failures (401 auth, 402 credits, 429 rate limit, network errors) must produce readable error messages, not stack traces. | Low | Check status codes. Raise RuntimeError with human-readable messages. Reference project has good patterns. |
| **ComfyUI Manager installation** | Users expect to install via "Install via Git URL" in ComfyUI Manager. Proper `__init__.py` with `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`, plus `requirements.txt`. | Low | Standard pattern: `__init__.py` imports from node modules, merges mappings. Git repo with requirements.txt. |
| **Category grouping in node menu** | Users find nodes by right-clicking and browsing categories. All nodes should appear under a consistent category like "Seedance 2.0". | Low | Set `CATEGORY = "Seedance 2.0"` on all node classes. |

---

## Differentiators

Features that set this plugin apart from the reference project (muapi.ai version) and from other video generation plugins. These create competitive advantage.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Video Extend node** | Extend a previously generated video using its video ID. Allows creating longer videos than 15s by chaining. The reference project supports this. | Medium | Input: video_id from a completed generation. Optional continuation prompt. AIHubMix API endpoint: reuse `POST /v1/videos` with the video_id reference. Need to verify exact extend semantics on AIHubMix vs muapi.ai. |
| **Omni Reference node** | Combine images, video clips, and audio as multi-modal inputs. This is Seedance 2.0's signature capability -- no other plugin supports this combination. | High | Up to 9 images (as tensors), 3 video URLs, 3 audio URLs. Reference in prompt with `@image1`, `@video1`, `@audio1`. Need to verify AIHubMix supports the omni-reference payload format. |
| **Inline base64 image input** | AIHubMix supports direct base64 data URI in the `input` field -- no separate upload step. This is a DX advantage over muapi.ai which requires uploading to a separate endpoint first. Simpler, fewer API calls, less failure points. | Low | Convert ComfyUI IMAGE tensor to base64 JPEG in-memory. Include directly in JSON payload. Already validated in `seedance_video.py`. |
| **Video preview in ComfyUI UI** | Show the generated video as a playable preview in the ComfyUI canvas (not just a file on disk). The reference project's saver uses `OUTPUT_NODE = True` with `{"ui": {"gifs": [preview]}}` to display video in the node widget. | Medium | Set `OUTPUT_NODE = True` on Save Video node. Return `{"ui": {"gifs": [{"filename": ..., "subfolder": ..., "type": "output", "format": "video/mp4"}]}}` alongside the tensor result. This is the standard ComfyUI video preview pattern. |
| **1080p resolution support** | AIHubMix defaults to 1080p when size is omitted. The reference project (muapi.ai) only goes up to 720p for T2V. This is a tangible quality difference. | Low | When resolution is "1080p", omit the `size` parameter entirely and let the API default. No extra code needed. |
| **Clean error recovery** | Most API plugins crash on network errors. A robust retry-with-backoff pattern for transient failures (429, 503, timeouts) would be genuinely differentiated. | Medium | Add configurable retry count (default 3). Exponential backoff. Distinguish retryable vs non-retryable errors. |
| **Configurable poll interval** | Advanced users may want faster or slower polling. The reference hardcodes 10s; AIHubMix responses often update faster. | Low | Add a hidden/advanced `poll_interval` parameter. Default 5s (faster than reference). |
| **Example workflow JSON files** | Bundled workflow files that users can drag into ComfyUI to get started immediately. Lowers the barrier to first successful generation. | Low | Include 2-3 `.json` workflow files: T2V basic, I2V basic, Save Video. Embed workflow metadata in output video if possible (ComfyUI standard pattern). |

---

## Anti-Features

Features to explicitly NOT build. These add complexity without proportional value, or are actively harmful.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Consistent Character workflow** | Complex multi-step pipeline (character sheet generation + consistent video). The reference project has `Seedance2Character` and `Seedance2ConsistentVideo` nodes. The AIHubMix API may not support the same character sheet endpoints. Defer to v2. | Defer. Focus on core generation quality first. Add in v2 if users request it. |
| **Local model inference** | This is a cloud API plugin. Local inference would require shipping model weights, GPU management, and a completely different architecture. Not the product's purpose. | Cloud API only. Never bundle model weights. |
| **Environment variable / config file API key** | Adding env var and config file reading complicates the key resolution chain and makes debugging harder. The node-input-only pattern is simpler and more visible. | API key via node input only. The dedicated API Key node handles the "set once, wire everywhere" case. |
| **Image upload endpoint** | AIHubMix accepts images inline (base64 data URI in JSON payload). Adding a separate upload endpoint adds complexity with zero benefit. | Use inline base64 in the `input` field directly. |
| **Custom UI widgets** | Building custom JavaScript frontend widgets for ComfyUI adds a massive maintenance burden and breaks with ComfyUI updates. | Use standard ComfyUI input types (STRING, INT, FLOAT, COMBO, IMAGE). The node category and display names provide enough branding. |
| **Multiple API provider support** | Supporting muapi.ai, fal.ai, Volcengine, etc. in the same plugin creates branching code paths and testing complexity. | AIHubMix only. Clean, single-provider implementation. Users who want other providers can use the reference project. |
| **Video-to-video / video editing** | Seedance 2.0 supports video editing capabilities, but the AIHubMix API surface for this is unclear and the workflow is complex. | Defer. Focus on T2V, I2V, Extend, Omni. |
| **Audio generation** | Seedance 2.0 natively generates audio, but exposing audio control parameters adds UI complexity for uncertain AIHubMix API support. | Let the model generate audio automatically. Do not expose audio control parameters in v1. |
| **Batch generation** | Submitting multiple video requests in parallel adds queue management complexity and can hit rate limits. | One video per node execution. Users who want batch can use ComfyUI's queue system. |

---

## Feature Dependencies

```
API Key Node --> Text-to-Video Node --> Save Video Node
API Key Node --> Image-to-Video Node --> Save Video Node
API Key Node --> Omni Reference Node --> Save Video Node

Text-to-Video Node --> (video_id) --> Video Extend Node --> Save Video Node
Image-to-Video Node --> (video_id) --> Video Extend Node --> Save Video Node
Omni Reference Node --> (video_id) --> Video Extend Node --> Save Video Node

Save Video Node --> (IMAGE tensor) --> [any downstream node: Preview, Upscale, VHS, etc.]
```

**Dependency chain rationale:**
- API Key Node is standalone but feeds into all generation nodes.
- Generation nodes are independent of each other (user picks T2V, I2V, or Omni).
- Video Extend depends on a video_id from a prior generation.
- Save Video is the universal sink -- it takes a video_url from any generation node.
- All generation nodes output video_url + first_frame + video_id, enabling both immediate preview and extend workflows.

---

## MVP Recommendation

### Phase 1 -- Core Generation (Ship First)
1. **API Key Node** -- table stakes, every workflow needs it
2. **Text-to-Video Node** -- core value proposition, simplest to implement
3. **Image-to-Video Node** -- second most requested feature, same API pattern
4. **Save Video Node** -- required to get output out of ComfyUI (disk save + IMAGE tensor + UI preview)
5. **Resolution / Aspect Ratio / Duration controls** -- built into T2V and I2V nodes

### Phase 2 -- Advanced Capabilities
6. **Video Extend Node** -- depends on video_id output from Phase 1 nodes
7. **Omni Reference Node** -- multi-modal input, higher complexity, smaller user base
8. **Example workflow JSON files** -- lowers onboarding friction

### Defer to v2
- Consistent Character workflow
- Audio control parameters
- Video editing
- Multi-provider support
- Batch generation

---

## Node Inventory (Final)

| Node Name | Display Name | Inputs | Outputs | Category |
|-----------|-------------|--------|---------|----------|
| `SeedanceApiKey` | "Seedance 2.0 API Key" | api_key (STRING) | api_key (STRING) | Seedance 2.0 |
| `SeedanceTextToVideo` | "Seedance 2.0 Text-to-Video" | prompt, size, seconds, api_key (opt) | video_url (STRING), first_frame (IMAGE), video_id (STRING) | Seedance 2.0 |
| `SeedanceImageToVideo` | "Seedance 2.0 Image-to-Video" | prompt, image (IMAGE), size, seconds, api_key (opt) | video_url (STRING), first_frame (IMAGE), video_id (STRING) | Seedance 2.0 |
| `SeedanceExtend` | "Seedance 2.0 Extend Video" | video_id, prompt (opt), size, seconds, api_key (opt) | video_url (STRING), first_frame (IMAGE), new_video_id (STRING) | Seedance 2.0 |
| `SeedanceOmniReference` | "Seedance 2.0 Omni Reference" | prompt, images (up to 9), video_urls (up to 3), audio_urls (up to 3), size, seconds, api_key (opt) | video_url (STRING), first_frame (IMAGE), video_id (STRING) | Seedance 2.0 |
| `SeedanceSaveVideo` | "Seedance 2.0 Save Video" | video_url (STRING), filename_prefix, frame_load_cap (opt), skip_first_frames (opt), select_every_nth (opt) | frames (IMAGE), filepath (STRING), frame_count (INT) | Seedance 2.0 |

**Total nodes: 6** (4 generation + 1 API key + 1 save)

---

## API Parameter Mapping

### AIHubMix Video Generation (`POST /v1/videos`)

| Parameter | Type | Required | Values | Notes |
|-----------|------|----------|--------|-------|
| `model` | STRING | Yes | `"doubao-seedance-2-0-260128"` | Fixed model ID |
| `prompt` | STRING | Yes | Any text | Natural language video description |
| `size` | STRING | No | See size map below | Omit for 1080p default |
| `seconds` | INT | No | 4-15 (default 5) | Duration in seconds |
| `input` | STRING | No | URL, base64 data URI, or file | Reference image for I2V |

### Size Map (Resolution x Aspect Ratio)

| Resolution | 16:9 | 9:16 | 4:3 | 3:4 | 1:1 | 21:9 |
|-----------|------|------|-----|-----|-----|------|
| **480p** | 832x480 | 480x832 | 640x480 | 480x640 | 624x624 | 1120x480 |
| **720p** | 1280x720 | 720x1280 | 960x720 | 720x960 | 960x960 | 1680x720 |
| **1080p** | (omit size param -- API defaults to 1080p) | | | | | |

### API Response Format

**Create video response:**
```json
{
  "id": "video_abc123",
  "status": "queued",
  "model": "doubao-seedance-2-0-260128"
}
```

**Poll status response:**
```json
{
  "id": "video_abc123",
  "status": "in_progress",
  "progress": 45.2
}
```

**Completed response:**
```json
{
  "id": "video_abc123",
  "status": "completed",
  "output": { "url": "https://..." }
}
```

**Download:** `GET /v1/videos/{id}/content` (streaming, returns video bytes)

---

## ComfyUI Node UX Patterns (Reference)

Based on analysis of the reference project, Runway official nodes, and ComfyUI built-in nodes:

| Pattern | Implementation | Source |
|---------|---------------|--------|
| **API key as optional STRING** | `"api_key": ("STRING", {"multiline": False, "default": ""})` in `optional` inputs. Falls back to error if not provided. | Reference project |
| **OUTPUT_NODE for video preview** | Set `OUTPUT_NODE = True`. Return `{"ui": {"gifs": [{"filename": ..., "subfolder": ..., "type": "output", "format": "video/mp4"}]}, "result": (...)}` | Reference project saver node, ComfyUI built-in SaveVideo |
| **IMAGE tensor format** | `torch.Tensor` with shape `[B, H, W, C]`, dtype `float32`, values 0.0-1.0, RGB order | ComfyUI standard |
| **Category naming** | `CATEGORY = "Seedance 2.0"` -- nodes appear under this in the right-click menu | Reference project uses emoji prefix; simpler without |
| **Display name mapping** | `NODE_DISPLAY_NAME_MAPPINGS = {"ClassName": "Display Name"}` in `__init__.py` | ComfyUI standard |
| **Console logging** | `print(f"[Seedance2 T2V] Submitting...")` prefix pattern for server log visibility | Reference project |
| **Multiline prompt** | `("STRING", {"multiline": True, "default": "..."})` for prompt inputs | Standard across all text-gen nodes |
| **Tooltip support** | `("STRING", {..., "tooltip": "..."})` for user guidance | ComfyUI feature |

---

## Sources

- [Reference project source code](https://github.com/Anil-matcha/seedance2-comfyui) -- `seedance2_nodes.py`, `seedance2_video_saver.py`, `__init__.py` (cloned and read directly)
- [AIHubMix Video Generation API docs](https://docs.aihubmix.com/en/api/Video-Gen) -- endpoint, parameters, examples
- [Seedance 2.0 official page](https://seed.bytedance.com/en/seedance2_0) -- model capabilities
- [ComfyUI Runway Partner Nodes tutorial](https://docs.comfy.org/tutorials/partner-nodes/runway/video-generation) -- official API node UX patterns
- [ComfyUI Partner Nodes overview](https://docs.comfy.org/tutorials/partner-nodes/overview) -- API node architecture
- [ComfyUI SaveVideo built-in node docs](https://docs.comfy.org/built-in-nodes/SaveVideo) -- video output handling
- [ComfyUI custom node lifecycle](https://docs.comfy.org/custom-nodes/backend/lifecycle) -- NODE_CLASS_MAPPINGS pattern
- [ComfyUI-Manager publishing guide](https://docs.comfy.org/custom-nodes/backend/manager) -- installation patterns
- [Seedance 2.0 on fal.ai](https://fal.ai/seedance-2.0) -- model capability details
- [Test script `seedance_video.py`](file://C:/WorkSpace/seedance_comfyui/seedance_video.py) -- validated API parameter map and flow

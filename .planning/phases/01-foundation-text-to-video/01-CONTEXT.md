# Phase 1: Foundation + Text-to-Video - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Plugin scaffolding, AIHubMix API client, API key management, and text-to-video generation node. Users can enter their AIHubMix API key and generate a video from a text prompt inside ComfyUI, receiving a video URL and video ID.

This phase does NOT include: image-to-video, video download/save/preview, video extend, or omni reference.

</domain>

<decisions>
## Implementation Decisions

### T2V Output Strategy
- **D-01:** T2V node outputs `video_url` (STRING) and `video_id` (STRING) only. No first_frame extraction in Phase 1.
- **D-02:** `first_frame` (IMAGE) output is deferred to Phase 2 Save Video node, which will handle video download and frame extraction.

### Progress Feedback
- **D-03:** API polling progress is shown via print/console logging to ComfyUI log window. No ComfyUI Web UI progress bar integration in Phase 1.
- **D-04:** Follow the test script pattern — periodic status updates with progress percentage printed to console.

### API Key Node UX
- **D-05:** API Key node is a simple string passthrough — accepts STRING input and returns it as output for wiring to generation nodes.
- **D-06:** T2V node has an optional `api_key` field as fallback when not wired from the API Key node.
- **D-07:** No key format validation or masking — keep it simple for v1.

### Error Message Style
- **D-08:** Error messages include both the API error and actionable suggestions. Examples:
  - 401: "认证失败：请检查你的 API 密钥是否正确，可在 aihubmix.com 查看"
  - 402: "余额不足：请到 aihubmix.com 充值"
  - 429: "请求过于频繁：请稍后重试"
  - Network: "网络连接失败：请检查网络设置"
- **D-09:** Use Python exceptions (raise) to surface errors in ComfyUI — this is the standard ComfyUI error mechanism.

### Claude's Discretion
- File/module structure and naming conventions
- API client implementation details (class vs functions, retry logic, timeout values)
- SIZE_MAP data structure (reuse from test script)
- Node parameter definitions (INT vs FLOAT for duration, enum choices for resolution/ratio)
- Polling interval (5 seconds per test script)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### API Reference
- `seedance_video.py` — Proven test script with complete AIHubMix API interaction pattern (create, poll, download, SIZE_MAP, error handling). The API client module should follow this pattern closely.

### External API Docs
- AIHubMix Video Gen API: https://docs.aihubmix.com/en/api/Video-Gen — endpoint specifications, request/response format, supported parameters
- Model ID: `doubao-seedance-2-0-260128`

### ComfyUI Reference
- ComfyUI Custom Node Walkthrough: https://docs.comfy.org/custom-nodes/walkthrough — NODE_CLASS_MAPPINGS registration, node structure
- ComfyUI Tensors: https://docs.comfy.org/custom-nodes/backend/tensors — IMAGE format [B,H,W,C] float32 in [0.0, 1.0]

### Reference Project
- https://github.com/Anil-matcha/seedance2-comfyui — Original muapi.ai-based implementation to fork/adapt. Provides ComfyUI node framework, tensor conversion patterns, and node registration structure.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `seedance_video.py`: Complete AIHubMix API interaction pattern — SIZE_MAP (resolution/ratio mapping), create_video (POST /v1/videos), wait_for_video (polling loop with progress), resolve_image_reference (base64 encoding). This is the primary reference for the API client module.
- Reference project (seedance2-comfyui): ComfyUI node structure, __init__.py registration pattern, VIDEO_SAVER node, tensor conversion utilities.

### Established Patterns
- API authentication: `Authorization: Bearer {key}` header
- Video creation: POST to `/v1/videos` with model, prompt, seconds, size, and optional input fields
- Polling: GET `/v1/videos/{id}` every 5 seconds, status transitions: queued → in_progress → completed/failed
- Resolution handling: SIZE_MAP for 480p/720p combos, None (omit size field) for 1080p default

### Integration Points
- `__init__.py`: ComfyUI loads custom nodes from this file. Must export NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS.
- Node category: "Seedance 2.0" — all nodes appear under this category in ComfyUI node menu.
- ComfyUI execution model: Synchronous — node `run()` method blocks until it returns. No async needed.

</code_context>

<specifics>
## Specific Ideas

- Error messages should be in Chinese (matching user's language preference) with technical details (status code, API response) for debugging.
- T2V node parameters should match the test script's CLI arguments: prompt (required), duration (4-15, default 5), resolution (480p/720p/1080p), ratio (16:9/9:16/4:3/3:4/1:1/21:9).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-foundation-text-to-video*
*Context gathered: 2026-04-03*

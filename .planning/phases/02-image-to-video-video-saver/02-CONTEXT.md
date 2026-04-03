# Phase 2: Image-to-Video + Video Saver - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

I2V node (image-to-video with reference image input + prompt), Save Video node (download generated video, extract frames as IMAGE tensor, preview in ComfyUI UI). Users can generate videos from reference images and download/preview the results as ComfyUI tensors.

This phase does NOT include: Video Extend, Omni Reference, or GitHub publishing.

</domain>

<decisions>
## Implementation Decisions

### I2V Output Strategy
- **D-10:** I2V node outputs `(video_url: STRING, video_id: STRING)` — same format as T2V. Consistent with Phase 1 D-01.
- **D-11:** first_frame extraction is handled by the Save Video node (Phase 2), not by I2V.

### Save Video Node Design
- **D-12:** Save Video outputs `(IMAGE, STRING, STRING)` = `(frames, first_frame_path, video_path)`.
  - `frames`: All extracted video frames as ComfyUI IMAGE tensor (limited by frame_load_cap).
  - `first_frame_path`: File path to the saved first frame image.
  - `video_path`: File path to the downloaded video file.
- **D-12a:** `frame_load_cap` defaults to 16. User can adjust. Prevents OOM on long videos.
- **D-12b:** Save Video is an OUTPUT_NODE = True (terminal node, triggers video download and UI preview).
- **D-12c:** Video preview uses ComfyUI's OUTPUT_NODE + preview mechanism (gifs/video in UI canvas).

### Image Conversion
- **D-13:** ComfyUI IMAGE tensor (B,H,W,C float32 [0,1]) → JPEG quality=95 → base64 data URI for API upload.
  - Conversion: float32 → uint8 via `np.clip(tensor * 255, 0, 255).astype(np.uint8)` → PIL Image → JPEG bytes → base64 data URI.
  - Uses `data:image/jpeg;base64,{encoded}` format (matches test script `encode_image_to_base64` pattern).

### Claude's Discretion
- `api_client.py` I2V extension method (new `create_i2v_video` / `create_and_wait_i2v` functions or extend existing)
- Video download implementation (requests streaming to ComfyUI output directory)
- Frame extraction implementation details (opencv VideoCapture, frame skipping strategy)
- Save Video filename generation (timestamp/uuid/sequential)
- Save Video subfolder handling (create if not exists)
- I2V node parameter layout (grouping of image input + generation params)

### Folded Todos
None — no pending todos matched this phase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### API Reference
- `seedance_video.py` — Proven test script. Key functions for Phase 2:
  - `resolve_image_reference()` — validates and converts image ref (URL/local/data URI)
  - `encode_image_to_base64()` — local file → base64 data URI pattern
  - `create_video()` with `image_reference` parameter — shows API payload format: `payload["input"] = resolve_image_reference(ref)`
  - `download_video()` — streaming download pattern with progress

### Existing Implementation (Phase 1)
- `api_client.py` — Must be EXTENDED (not rewritten) with I2V support. Contains `create_video`, `wait_for_video`, `create_and_wait`, `SIZE_MAP`, `_get_headers`, `_check_response`.
- `nodes.py` — Pattern reference for I2V and Save Video node class structure (CATEGORY, INPUT_TYPES, RETURN_TYPES, FUNCTION, OUTPUT_NODE).
- `__init__.py` — Must be UPDATED to register new I2V and Save Video node classes in NODE_CLASS_MAPPINGS.
- `tests/conftest.py` — Shared test fixtures (mock_api_key, mock_video_response, etc.) to reuse.

### External API Docs
- AIHubMix Video Gen API: https://docs.aihubmix.com/en/api/Video-Gen — I2V uses same POST /v1/videos endpoint with `input` field for image reference
- Model ID: `doubao-seedance-2-0-260128`

### ComfyUI Reference
- ComfyUI Custom Node Walkthrough: https://docs.comfy.org/custom-nodes/walkthrough — NODE_CLASS_MAPPINGS registration
- ComfyUI Tensors: https://docs.comfy.org/custom-nodes/backend/tensors — IMAGE format [B,H,W,C] float32 in [0.0, 1.0]

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `api_client.py`: Full API communication layer. I2V needs a new function that adds `input` (image base64) to the payload. The `create_video` function can be extended or a new `create_i2v_video` can be added.
- `seedance_video.py` `resolve_image_reference`: Already handles URL/local/data URI image inputs. The base64 encoding pattern is proven.
- `seedance_video.py` `download_video`: Streaming download with progress. Pattern for Save Video node's download logic.
- `nodes.py` `SeedanceTextToVideo`: Template for I2V node structure — same CATEGORY, similar INPUT_TYPES pattern, same api_key handling.
- `tests/conftest.py`: Mock fixtures for API responses. Can be extended for I2V-specific responses.

### Established Patterns
- Function-based API client (not class) — per Phase 1 decision
- Node classes: CATEGORY = "Seedance 2.0", @classmethod INPUT_TYPES, RETURN_TYPES tuple, FUNCTION string, OUTPUT_NODE bool
- API key validation: `if not api_key: raise ValueError(...)` at start of generate method
- Error handling: RuntimeError with Chinese messages per D-08
- SIZE_MAP for resolution/ratio mapping, reused from Phase 1

### Integration Points
- `__init__.py`: Add `SeedanceImageToVideo` and `SeedanceSaveVideo` to imports and mappings
- `api_client.py`: Add I2V-specific create function (accepts image data alongside prompt)
- `nodes.py`: Add two new node classes that import from api_client
- Video download: ComfyUI `folder_paths.get_output_directory()` for output path
- Frame extraction: opencv `cv2.VideoCapture` for reading downloaded video frames

</code_context>

<specifics>
## Specific Ideas

- I2V node should accept IMAGE tensor as required input (not optional — the whole point is reference image)
- Save Video node should save first frame as a separate PNG file for easy access
- Error messages should continue to be in Chinese per Phase 1 D-08
- The `input` field in the API payload accepts base64 data URIs (proven in test script)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-image-to-video-video-saver*
*Context gathered: 2026-04-03*

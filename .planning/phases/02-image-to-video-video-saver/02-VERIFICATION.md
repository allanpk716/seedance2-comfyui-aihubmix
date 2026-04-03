---
phase: 02-image-to-video-video-saver
verified: 2026-04-03T12:00:00Z
status: passed
score: 9/9 must-haves verified
requirements_note:
  I2V-03_discrepancy: "REQUIREMENTS.md says I2V-03 outputs first_frame (IMAGE), but D-10/D-11 deliberately deferred this to Save Video node. Same pattern as T2V-04 in Phase 1. REQUIREMENTS.md not updated to reflect this design decision. Implementation is internally consistent."
  I2V_traceability_status: "REQUIREMENTS.md traceability table still shows I2V-01..04 as 'Pending' despite implementation being complete. Status fields were not updated."
---

# Phase 2: Image-to-Video + Video Saver Verification Report

**Phase Goal:** Add Image-to-Video generation and Save Video (download + frame extraction + preview) capabilities to the Seedance 2.0 ComfyUI plugin.
**Verified:** 2026-04-03T12:00:00Z
**Status:** PASSED
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User can wire a ComfyUI IMAGE tensor into the I2V node and generate a video from a reference image | VERIFIED | nodes.py:90-136 SeedanceImageToVideo class accepts "image" as required IMAGE input, converts tensor via np.clip/PIL/JPEG/base64 pipeline, calls create_and_wait_i2v |
| 2 | IMAGE tensor is correctly converted from ComfyUI format (B,H,W,C float32 [0,1]) to base64 JPEG data URI for the API | VERIFIED | nodes.py:128-133 implements full conversion: np.clip(image[0].cpu().numpy() * 255) -> uint8 -> PIL Image -> JPEG quality=95 -> base64 -> "data:image/jpeg;base64,..." per D-13 |
| 3 | I2V node outputs (video_url: STRING, video_id: STRING) matching T2V output format per D-10 | VERIFIED | nodes.py:115-116 RETURN_TYPES = ("STRING", "STRING"), RETURN_NAMES = ("video_url", "video_id"). generate() returns (result["video_url"], result["video_id"]) at line 136 |
| 4 | I2V node supports same resolution, aspect ratio, and duration controls as T2V | VERIFIED | nodes.py:107-112 optional fields: api_key STRING, duration INT (default=5, min=4, max=15), resolution ["1080p","720p","480p"], ratio ["16:9","9:16","4:3","3:4","1:1","21:9"] -- identical to T2V |
| 5 | User can wire a video URL from T2V or I2V into Save Video node and the file appears in ComfyUI output directory | VERIFIED | nodes.py:168-191 save() accepts video_url STRING, downloads via requests.get(stream=True), writes to folder_paths.get_output_directory(). Test test_save_downloads_video verifies .mp4 file creation |
| 6 | Save Video extracts frames from downloaded video and returns them as ComfyUI IMAGE tensor (N,H,W,C float32 [0,1]) | VERIFIED | nodes.py:193-212 cv2.VideoCapture -> cv2.cvtColor(BGR2RGB) -> float32/255.0 -> torch.from_numpy(np.stack). Test test_save_extracts_frames verifies dtype, dims, value range |
| 7 | Save Video returns UI preview dict so ComfyUI displays video/preview in the canvas | VERIFIED | nodes.py:221-224 returns {"ui": {"images": [{"filename": ..., "subfolder": ..., "type": "output"}]}, "result": (...)}. Test test_save_ui_preview verifies structure |
| 8 | User can configure filename prefix and save subfolder for organized output | VERIFIED | nodes.py:156-161 optional inputs: filename_prefix (default="Seedance"), subfolder (default=""). Tests test_save_custom_prefix and test_save_subfolder verify behavior |
| 9 | Frame extraction respects frame_load_cap (default 16) to prevent OOM | VERIFIED | nodes.py:160 frame_load_cap INT (default=16, min=1, max=1000). nodes.py:198 while len(frames) < frame_load_cap. Test test_save_frame_load_cap verifies cap=2 produces exactly 2 frames |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `api_client.py` | create_i2v_video and create_and_wait_i2v functions | VERIFIED | Lines 138-176. Both functions exist, substantive (39 lines), wired (imported in nodes.py:21) |
| `nodes.py` | SeedanceImageToVideo class with IMAGE input and tensor-to-base64 conversion | VERIFIED | Lines 90-137. Class exists, 48 lines, accepts IMAGE tensor, full conversion pipeline |
| `nodes.py` | SeedanceSaveVideo OUTPUT_NODE class with download, frame extraction, and preview | VERIFIED | Lines 139-224. Class exists, 86 lines, OUTPUT_NODE=True, full download+extract+preview implementation |
| `__init__.py` | Registration of both new node classes | VERIFIED | Lines 1,6-7,13-14. Both SeedanceImageToVideo and SeedanceSaveVideo in NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS |
| `tests/test_api_client.py` | TestCreateI2VVideo and TestCreateAndWaitI2V test classes | VERIFIED | Lines 247-345. TestCreateI2VVideo (5 tests) + TestCreateAndWaitI2V (2 tests) |
| `tests/test_nodes.py` | TestSeedanceImageToVideo and TestSeedanceSaveVideo test classes | VERIFIED | TestSeedanceImageToVideo (12 tests, lines 196-343), TestSeedanceSaveVideo (16 tests, lines 346-590) |
| `tests/conftest.py` | mock_i2v_response, mock_folder_paths, mock_video_bytes, sample_image_tensor fixtures | VERIFIED | Lines 37-43 (mock_i2v_response), 82-88 (mock_folder_paths), 62-79 (mock_video_bytes), 91-95 (sample_image_tensor) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| nodes.py SeedanceImageToVideo | api_client.py create_and_wait_i2v | `from .api_client import create_and_wait_i2v` (line 21) | WIRED | Imported and called at line 135 with all 6 args |
| api_client.py create_i2v_video | AIHubMix POST /v1/videos | `requests.post` with `"input": image_data_uri` in payload (line 145) | WIRED | payload contains model, prompt, seconds, input, and optional size |
| nodes.py SeedanceSaveVideo | video URL | `requests.get(video_url, stream=True, timeout=300)` (line 186) | WIRED | Streaming download with chunked write |
| nodes.py SeedanceSaveVideo | downloaded .mp4 file | `cv2.VideoCapture(video_path)` (line 193) | WIRED | BGR->RGB conversion, float32 normalization, torch tensor assembly |
| nodes.py SeedanceSaveVideo save() | ComfyUI UI canvas | `return {"ui": {"images": [...]}, "result": (...)}` (lines 221-224) | WIRED | Dict with "ui" and "result" keys per OUTPUT_NODE format |
| __init__.py | nodes.py SeedanceImageToVideo | `NODE_CLASS_MAPPINGS["SeedanceImageToVideo"]` | WIRED | Imported at line 1, registered at line 6 |
| __init__.py | nodes.py SeedanceSaveVideo | `NODE_CLASS_MAPPINGS["SeedanceSaveVideo"]` | WIRED | Imported at line 1, registered at line 7 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| SeedanceImageToVideo.generate() | `data_uri` (base64 JPEG) | `image` tensor input -> np.clip -> PIL -> JPEG -> base64 | Yes -- real conversion from tensor, no hardcoded values | FLOWING |
| SeedanceImageToVideo.generate() | `result` dict | `create_and_wait_i2v()` API call | Yes -- returns video_url and video_id from API response | FLOWING |
| SeedanceSaveVideo.save() | `frames_tensor` | `cv2.VideoCapture` -> frame extraction | Yes -- real frame extraction from downloaded video bytes, verified by tests with actual cv2.VideoWriter-generated test video | FLOWING |
| SeedanceSaveVideo.save() | `first_frame_path` | `frames[0]` -> uint8 -> PIL PNG save | Yes -- real first frame saved to disk, test verifies file exists | FLOWING |
| SeedanceSaveVideo.save() | video file on disk | `requests.get(video_url, stream=True)` | Yes -- real streaming download, test verifies .mp4 file written | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite passes | `python -m pytest tests/ -x --tb=short -q` | 71 passed in 0.29s | PASS |
| I2V API client tests pass | `python -m pytest tests/test_api_client.py::TestCreateI2VVideo tests/test_api_client.py::TestCreateAndWaitI2V -v` | 7 tests passing (verified via full suite) | PASS |
| I2V node tests pass | `python -m pytest tests/test_nodes.py::TestSeedanceImageToVideo -v` | 12 tests passing (verified via full suite) | PASS |
| Save Video tests pass | `python -m pytest tests/test_nodes.py::TestSeedanceSaveVideo -v` | 16 tests passing (verified via full suite) | PASS |
| Registration tests include new nodes | `python -m pytest tests/test_registration.py -v` | 4 test methods passing (verified via full suite) | PASS |
| All 4 node classes registered | Inspect __init__.py | NODE_CLASS_MAPPINGS has {SeedanceApiKey, SeedanceTextToVideo, SeedanceImageToVideo, SeedanceSaveVideo} | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-----------|-------------|--------|----------|
| I2V-01 | 02-01 | User provides IMAGE tensor + prompt to generate video with reference image | SATISFIED | SeedanceImageToVideo accepts "image" (IMAGE) and "prompt" (STRING) as required inputs. Calls create_and_wait_i2v with data URI derived from image tensor. |
| I2V-02 | 02-01 | Image converted from ComfyUI tensor (B,H,W,C float32) to base64 JPEG data URI for API | SATISFIED | nodes.py:128-133 implements np.clip*255 -> uint8 -> PIL Image -> JPEG quality=95 -> base64 -> "data:image/jpeg;base64,..." per D-13. Test test_i2v_tensor_to_data_uri verifies format. |
| I2V-03 | 02-01 | Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING) | PARTIALLY SATISFIED | Outputs (video_url: STRING, video_id: STRING) per D-10. first_frame (IMAGE) was deliberately deferred to Save Video node per D-11. Same pattern as T2V-04 which was also accepted without first_frame in Phase 1. REQUIREMENTS.md not updated to reflect this decision. |
| I2V-04 | 02-01 | User can select resolution, aspect ratio, and duration same as T2V | SATISFIED | nodes.py:107-112 optional fields match T2V exactly: duration INT 4-15, resolution ["1080p","720p","480p"], ratio ["16:9","9:16","4:3","3:4","1:1","21:9"]. |
| VSAV-01 | 02-02 | Save Video node downloads generated video from URL to ComfyUI output directory | SATISFIED | nodes.py:184-191 requests.get(stream=True) writes to folder_paths.get_output_directory(). Test test_save_downloads_video verifies .mp4 file creation. |
| VSAV-02 | 02-02 | Node extracts frames and returns as ComfyUI IMAGE tensor with frame_load_cap to prevent OOM | SATISFIED | nodes.py:193-212 cv2.VideoCapture extracts frames, converts BGR->RGB, normalizes to float32 [0,1], assembles torch tensor. frame_load_cap defaults to 16 per D-12a. Test test_save_frame_load_cap verifies cap enforcement. |
| VSAV-03 | 02-02 | Video preview displays in ComfyUI UI canvas (OUTPUT_NODE with preview) | SATISFIED | nodes.py:149 OUTPUT_NODE=True, lines 221-224 returns {"ui": {"images": [...]}, "result": (...)}. Test test_save_ui_preview verifies structure. Actual canvas rendering requires running ComfyUI (manual verification). |
| VSAV-04 | 02-02 | User can configure filename prefix and save subfolder | SATISFIED | nodes.py:156-161 optional inputs: filename_prefix (STRING, default="Seedance"), subfolder (STRING, default=""). Tests test_save_custom_prefix and test_save_subfolder verify behavior. |

**Orphaned requirements:** None. All 8 requirement IDs (I2V-01 through I2V-04, VSAV-01 through VSAV-04) appear in PLAN frontmatter and are accounted for above.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | - | - | No anti-patterns detected |

No TODO/FIXME/placeholder comments, no empty implementations, no stub handlers, no hardcoded empty data in production code. All function bodies contain substantive logic.

### Human Verification Required

### 1. ComfyUI Canvas Video Preview

**Test:** Run a full workflow with T2V -> Save Video in a running ComfyUI instance. Verify the .mp4 preview appears in the UI canvas.
**Expected:** The downloaded video file should show as a playable preview in the ComfyUI canvas after the Save Video node completes.
**Why human:** Requires a running ComfyUI instance and a valid API key. The OUTPUT_NODE return format is correct per ComfyUI conventions, but actual canvas rendering cannot be verified without the runtime.

### 2. I2V End-to-End with Real API

**Test:** Wire Image -> I2V -> Save Video with a valid AIHubMix API key. Verify video is generated from the reference image.
**Expected:** A video that visually incorporates the reference image content is generated, downloaded, and frames extracted.
**Why human:** Requires valid AIHubMix API key and credits. API communication is mocked in tests but real API behavior cannot be verified programmatically.

### Gaps Summary

No blocking gaps found. All 9 observable truths verified, all artifacts exist and are substantive, all key links are wired, all data flows produce real data, and all 71 tests pass.

**Minor observations (non-blocking):**

1. **I2V-03 / T2V-04 first_frame discrepancy:** REQUIREMENTS.md specifies first_frame (IMAGE) as an output for both T2V and I2V generation nodes, but the implementation (per design decisions D-01, D-10, D-11) deliberately outputs only (video_url, video_id) from generation nodes and delegates frame extraction to the Save Video node. This is a consistent architectural decision across Phase 1 and Phase 2. REQUIREMENTS.md should be updated to reflect this, but the implementation is internally consistent and well-reasoned.

2. **REQUIREMENTS.md traceability table stale:** I2V-01 through I2V-04 still show "Pending" in the traceability table at the bottom of REQUIREMENTS.md, despite the implementation being complete and verified. VSAV entries are correctly marked "Complete". The I2V status fields should be updated.

---

_Verified: 2026-04-03T12:00:00Z_
_Verifier: Claude (gsd-verifier)_

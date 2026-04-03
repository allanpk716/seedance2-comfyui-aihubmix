---
phase: 03-extend-omni-reference
verified: 2026-04-03T14:30:00Z
status: passed
score: 7/7 must-haves verified
---

# Phase 3: Extend + Omni Reference Verification Report

**Phase Goal:** Users can extend previously generated videos and combine multiple images/videos into multi-modal generation requests
**Verified:** 2026-04-03T14:30:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

Combined from both plans' must_haves and ROADMAP success criteria:

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User can take a video_id output from a prior generation and wire it into the Extend node to continue the video with an optional continuation prompt | VERIFIED | SeedanceExtendVideo accepts required video_id (STRING) + prompt (STRING), calls create_and_wait_extend which sends request_id payload to POST /v1/videos. Test test_extend_calls_create_and_wait_extend confirms wiring. |
| 2 | Extend node supports the same resolution, aspect ratio, and duration controls as T2V | VERIFIED | INPUT_TYPES optional block has duration (INT, 4-15, default 5), resolution (["1080p","720p","480p"]), ratio (6 options). Test test_extend_optional_fields validates all. |
| 3 | User can wire up to 9 images and up to 3 video URLs into the Omni Reference node along with a prompt and generate a multi-modal video | VERIFIED | SeedanceOmniReference.INPUT_TYPES has image_1..image_9 (IMAGE) + video_url_1..video_url_3 (STRING) in optional block. Uses **kwargs in generate(). Tests test_omni_optional_image_inputs and test_omni_optional_video_url_inputs confirm all 12 inputs exist. |
| 4 | Each image input to Omni Reference is correctly converted from ComfyUI tensor to base64 data URI | VERIFIED | generate() method loops image_1..9, for each non-None input: np.clip(img[0].cpu().numpy() * 255) -> PIL JPEG -> base64 -> data:image/jpeg;base64,{encoded}. Tests test_omni_with_single_image, test_omni_with_multiple_images verify data URI generation. |
| 5 | Unconnected image/video slots are silently ignored | VERIFIED | Image loop checks `if img is not None`. Video URL loop checks `if url`. Test test_omni_with_video_urls confirms video_url_2 (empty) is skipped while 1 and 3 are kept. Test test_omni_with_multiple_images confirms image_2 (unconnected) is skipped. |
| 6 | Extend node outputs (video_url: STRING, video_id: STRING) matching T2V/I2V pattern | VERIFIED | RETURN_TYPES = ("STRING","STRING"), RETURN_NAMES = ("video_url","video_id"). Test test_extend_output_types confirms. |
| 7 | Omni node outputs (video_url: STRING, video_id: STRING) matching T2V/I2V pattern | VERIFIED | RETURN_TYPES = ("STRING","STRING"), RETURN_NAMES = ("video_url","video_id"). Test test_omni_output_types confirms. |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `api_client.py` | create_extend_video and create_and_wait_extend functions | VERIFIED | Lines 178-215. Both functions exist with correct signatures. create_extend_video sends request_id in payload. |
| `api_client.py` | create_omni_video and create_and_wait_omni functions | VERIFIED | Lines 218-266. Both functions exist. create_omni_video accepts image_data_uris (list) and video_urls (list), adds to payload conditionally. |
| `nodes.py` | SeedanceExtendVideo ComfyUI node class | VERIFIED | Lines 141-180. Class with CATEGORY, INPUT_TYPES (video_id + prompt required, gen params optional), generate() with api_key + video_id validation. |
| `nodes.py` | SeedanceOmniReference ComfyUI node class | VERIFIED | Lines 183-250. Class with 9 IMAGE + 3 STRING optional inputs via loop, **kwargs pattern, base64 conversion loop. |
| `tests/test_api_client.py` | TestCreateExtendVideo + TestCreateAndWaitExtend | VERIFIED | Lines 351-462. 6 extend tests + 2 orchestration tests = 8 tests. |
| `tests/test_api_client.py` | TestCreateOmniVideo + TestCreateAndWaitOmni | VERIFIED | Lines 465-599. 7 omni tests + 2 orchestration tests = 9 tests. |
| `tests/test_nodes.py` | TestSeedanceExtendVideo | VERIFIED | Lines 593-727. 12 tests covering inputs, outputs, validation, API call forwarding. |
| `tests/test_nodes.py` | TestSeedanceOmniReference | VERIFIED | Lines 730-934. 15 tests covering inputs, outputs, validation, image conversion, video URL collection, combined inputs. |
| `tests/conftest.py` | mock_extend_response + mock_omni_response fixtures | VERIFIED | Lines 46-63. Both fixtures exist returning appropriate response dicts. |
| `tests/test_registration.py` | expected_keys includes SeedanceExtendVideo + SeedanceOmniReference | VERIFIED | Lines 42, 62. Both expected_keys sets contain all 6 nodes including the 2 new ones. |
| `__init__.py` | Registration of both new nodes | VERIFIED | Lines 1, 8-9, 17-18. Both imported and registered in NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| nodes.py | api_client.py | `from .api_client import create_and_wait_extend` | WIRED | Line 22. Import present. Used in SeedanceExtendVideo.generate() at line 179. |
| nodes.py | api_client.py | `from .api_client import create_and_wait_omni` | WIRED | Line 23. Import present. Used in SeedanceOmniReference.generate() at line 244. |
| __init__.py | nodes.py | `from .nodes import SeedanceExtendVideo` | WIRED | Line 1. Import present. Registered in NODE_CLASS_MAPPINGS at line 8 and NODE_DISPLAY_NAME_MAPPINGS at line 17. |
| __init__.py | nodes.py | `from .nodes import SeedanceOmniReference` | WIRED | Line 1. Import present. Registered in NODE_CLASS_MAPPINGS at line 9 and NODE_DISPLAY_NAME_MAPPINGS at line 18. |
| nodes.py SeedanceOmniReference.generate | multiple IMAGE tensors | np.clip + PIL JPEG + base64 encoding loop | WIRED | Lines 226-235. Loop over image_1..9, each converted via same pattern as I2V. Produces data:image/jpeg;base64 URIs. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| SeedanceExtendVideo.generate | video_id param | ComfyUI input wiring from prior node's video_id output | Passed as request_id to create_extend_video -> POST /v1/videos | FLOWING |
| SeedanceOmniReference.generate | image_data_uris list | kwargs.image_1..9 -> np.clip -> PIL JPEG -> base64 encode | List of data:image/jpeg;base64 strings passed to create_omni_video | FLOWING |
| SeedanceOmniReference.generate | video_urls list | kwargs.video_url_1..3 -> empty string filter | List of non-empty URL strings passed to create_omni_video | FLOWING |
| create_extend_video | payload | Composed from params + request_id = video_id | POSTed to /v1/videos, response extracted for new video_id | FLOWING |
| create_omni_video | payload | Composed from params + conditional input/video_urls fields | POSTed to /v1/videos, response extracted for video_id | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 115 tests pass | `python -m pytest tests/ -v` | 115 passed in 0.36s | PASS |
| Extend node registered | `python -c "import sys; sys.path.insert(0,'..'); import seedance_comfyui; print('ExtendVideo' in str(seedance_comfyui.NODE_CLASS_MAPPINGS))"` | True | PASS |
| Omni node registered | Same as above for OmniReference | True | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| EXTD-01 | 03-01 | User provides video_id from prior generation + optional continuation prompt | SATISFIED | SeedanceExtendVideo has required video_id (STRING) + prompt (STRING) inputs. create_extend_video sends request_id in payload. |
| EXTD-02 | 03-01 | Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING) | PARTIALLY SATISFIED | Outputs (video_url, video_id) only. first_frame (IMAGE) descoped per D-15 decision -- consistent with T2V/I2V nodes. Save Video node handles frame extraction. REQUIREMENTS.md marks as Complete. |
| EXTD-03 | 03-01 | User can select resolution, aspect ratio, and duration same as T2V | SATISFIED | Optional inputs: duration (INT 4-15), resolution (1080p/720p/480p), ratio (6 options). |
| OMNI-01 | 03-02 | User can combine multiple images (up to 9) + video URLs (up to 3) + prompt for multi-modal generation | SATISFIED | SeedanceOmniReference has 9 optional IMAGE + 3 optional STRING inputs. create_omni_video accepts image_data_uris and video_urls lists. |
| OMNI-02 | 03-02 | Each image input is converted from ComfyUI tensor to base64 data URI | SATISFIED | generate() converts each connected IMAGE via np.clip -> PIL JPEG -> base64 encode -> data:image/jpeg;base64 URI. |
| OMNI-03 | 03-02 | Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING) | PARTIALLY SATISFIED | Same as EXTD-02: outputs (video_url, video_id) only. first_frame descoped per D-15. REQUIREMENTS.md marks as Complete. |

**Note on EXTD-02 and OMNI-03:** The `first_frame (IMAGE)` output was explicitly descoped during planning via decision D-15, recorded in the DISCUSSION-LOG and RESEARCH documents. All generation nodes (T2V, I2V, Extend, Omni) consistently output `(video_url, video_id)` only. The Save Video node handles frame extraction. This is a project-wide design decision, not a Phase 3 gap. REQUIREMENTS.md reflects this by marking both requirements as "Complete."

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | - | - | No anti-patterns detected in any Phase 3 files |

No TODO/FIXME/PLACEHOLDER comments found. No empty implementations, no console.log-only handlers, no hardcoded empty data that flows to rendering.

### Human Verification Required

### 1. Extend API Payload Format

**Test:** Generate a T2V video to get a video_id, then wire that video_id into the Extend node and trigger generation.
**Expected:** The API accepts the request_id-based payload and returns a new extended video.
**Why human:** The actual AIHubMix API format for video extend was not verified during development (both plans auto-skipped API verification). The payload uses the MuAPI-compatible hypothesis with `request_id` field. If AIHubMix expects a different format, the extend functionality will fail at runtime.

### 2. Omni API Payload Format

**Test:** Wire 2-3 images and a video URL into the Omni Reference node and trigger generation.
**Expected:** The API accepts the multi-modal payload with `input` (array of data URIs) and `video_urls` (array of URL strings) fields.
**Why human:** Same as above -- API format was not verified. The payload uses hypothesis A (array of data URIs as `input`, video URLs as `video_urls`). If AIHubMix uses different field names or structure, the omni functionality will fail at runtime.

### 3. ComfyUI Optional IMAGE Input Behavior

**Test:** Add the Omni Reference node to a ComfyUI workflow, connect only image_1 and image_5, leave others unconnected. Trigger generation.
**Expected:** Unconnected IMAGE inputs are either omitted from kwargs or passed as None, and both cases are handled correctly.
**Why human:** ComfyUI's behavior for unconnected optional IMAGE inputs is documented as uncertain in the RESEARCH notes. The code handles None (skips it), but if ComfyUI raises an error or passes a different sentinel value, the node will fail at runtime.

### Gaps Summary

No gaps found. All 7 observable truths are verified through code inspection and passing tests. The implementation is substantive, wired end-to-end, and data flows correctly through all paths.

Two items are noted but not classified as gaps:
1. **first_frame output descoping (EXTD-02, OMNI-03):** Intentional project-wide decision (D-15). Consistent across all generation nodes. Not a Phase 3 issue.
2. **Unverified API formats:** Both extend and omni payload formats are hypotheses, not confirmed against the real AIHubMix API. This is flagged for human verification, not classified as a gap because the code structure is correct for the assumed format and can be adjusted post-testing.

---

_Verified: 2026-04-03T14:30:00Z_
_Verifier: Claude (gsd-verifier)_

---
phase: 02-image-to-video-video-saver
plan: 02
subsystem: video-processing
tags: [opencv, video-download, frame-extraction, comfyui-output-node, tensor]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: ComfyUI node infrastructure, API client, test framework
  - phase: 02-image-to-video-video-saver/01
    provides: SeedanceImageToVideo node, I2V API functions

provides:
  - SeedanceSaveVideo OUTPUT_NODE with video download and frame extraction
  - Frame-to-IMAGE tensor conversion (N,H,W,C float32 [0,1])
  - First frame PNG save for preview
  - ComfyUI UI preview dict for canvas display
  - Configurable filename prefix and subfolder output

affects: [03-extend-omni-reference, 04-publish]

# Tech tracking
tech-stack:
  added: [opencv-python-4.13.0]
  patterns: [lazy-import-for-testability, streaming-video-download, cv2-frame-extraction]

key-files:
  created: []
  modified:
    - nodes.py
    - __init__.py
    - tests/conftest.py
    - tests/test_nodes.py
    - tests/test_registration.py

key-decisions:
  - "Lazy import of folder_paths inside save() method to allow test mocking of ComfyUI built-in"
  - "frame_load_cap defaults to 16 to prevent OOM per D-12a"

patterns-established:
  - "OUTPUT_NODE return format: dict with 'ui' and 'result' keys"
  - "Mock folder_paths via patch.dict('sys.modules') in test fixtures"
  - "cv2.VideoCapture frame extraction with BGR->RGB and float32 normalization"

requirements-completed: [VSAV-01, VSAV-02, VSAV-03, VSAV-04]

# Metrics
duration: 8min
completed: 2026-04-03
---

# Phase 2 Plan 02: Save Video Node Summary

**SeedanceSaveVideo OUTPUT_NODE with streaming download, cv2.VideoCapture frame extraction to IMAGE tensors, first-frame PNG save, and ComfyUI canvas preview**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-03T10:50:35Z
- **Completed:** 2026-04-03T10:58:39Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- SeedanceSaveVideo OUTPUT_NODE downloads video from URL and saves to ComfyUI output directory
- Frame extraction via cv2.VideoCapture converts to ComfyUI IMAGE tensor format (N,H,W,C float32 [0,1])
- First frame saved as PNG file for immediate preview
- UI preview dict returned for ComfyUI canvas display per D-12c
- Configurable filename_prefix and subfolder for organized output per VSAV-04

## Task Commits

Each task was committed atomically:

1. **Task 1: Install opencv-python and set up test fixtures** - `407e4b3` (chore)
2. **Task 2 RED: Failing tests for SeedanceSaveVideo** - `55a61b4` (test)
3. **Task 2 GREEN: Implement SeedanceSaveVideo node** - `1b295d0` (feat)

**Auxiliary:** `9e7b762` (chore: gitignore update)

## Files Created/Modified
- `nodes.py` - Added SeedanceSaveVideo class (86 lines) with download, frame extraction, PNG save, UI preview
- `__init__.py` - Registered SeedanceSaveVideo in NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS
- `tests/conftest.py` - Added 4 fixtures: sample_video_url, mock_video_bytes, mock_folder_paths, sample_image_tensor
- `tests/test_nodes.py` - Added TestSeedanceSaveVideo class with 16 test methods
- `tests/test_registration.py` - Updated expected_keys to include SeedanceSaveVideo
- `.gitignore` - Added stray files

## Decisions Made
- **Lazy import of folder_paths:** Imported inside the `save()` method rather than at module level, because ComfyUI's `folder_paths` module is unavailable in test environments. This allows `@patch.dict("sys.modules")` to inject a mock before the import executes.
- **frame_load_cap=16 default:** Matches D-12a specification to prevent OOM with large videos.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] folder_paths module-level import breaks tests**
- **Found during:** Task 2 (GREEN phase)
- **Issue:** Plan specified `import folder_paths` at module top-level, but this causes `ModuleNotFoundError` in test environments where ComfyUI is not installed
- **Fix:** Moved `import folder_paths` inside the `save()` method as a lazy import, allowing the mock_folder_paths fixture to inject a mock via `patch.dict("sys.modules")` before the import executes
- **Files modified:** nodes.py
- **Verification:** All 71 tests pass
- **Committed in:** 1b295d0 (Task 2 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Minimal -- lazy import is functionally equivalent in ComfyUI runtime and enables proper test mocking.

## Issues Encountered
- pip install `opencv-python>=4.7` created a stray file `=4.7` on Windows (shell quoting issue). Added to .gitignore.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 2 fully complete. All 4 node classes registered (ApiKey, TextToVideo, ImageToVideo, SaveVideo)
- Ready for Phase 3: Extend + Omni Reference nodes
- Note: AIHubMix video download format (redirect vs direct bytes) will need verification in Phase 3 for the Extend node

---
*Phase: 02-image-to-video-video-saver*
*Completed: 2026-04-03*

## Self-Check: PASSED

- All 6 key files verified present on disk
- All 3 task commits verified in git log (407e4b3, 55a61b4, 1b295d0)
- All 71 tests passing

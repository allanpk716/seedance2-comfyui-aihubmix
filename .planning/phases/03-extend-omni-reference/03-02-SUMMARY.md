---
phase: 03-extend-omni-reference
plan: 02
subsystem: api, nodes
tags: [seedance, comfyui, omni-reference, multi-modal, base64, data-uri]

# Dependency graph
requires:
  - phase: 03-extend-omni-reference/01
    provides: create_extend_video/create_and_wait_extend pattern, SeedanceExtendVideo node class, test infrastructure
provides:
  - create_omni_video and create_and_wait_omni API client functions
  - SeedanceOmniReference ComfyUI node with 9 IMAGE + 3 video URL inputs
  - Full test coverage for omni reference (24 new tests)
affects: [phase-04-github-publication]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "**kwargs pattern for ComfyUI nodes with many optional inputs (image_1..image_9, video_url_1..video_url_3)"
    - "Loop-based INPUT_TYPES generation for numbered optional inputs"

key-files:
  created: []
  modified:
    - api_client.py
    - nodes.py
    - __init__.py
    - tests/conftest.py
    - tests/test_api_client.py
    - tests/test_nodes.py
    - tests/test_registration.py

key-decisions:
  - "Skipped API verification (auto-mode) -- using array of data URIs for images and video_urls field for video URLs"
  - "Used **kwargs in generate() to handle variable optional inputs from ComfyUI"

patterns-established:
  - "**kwargs pattern for variable optional inputs: ComfyUI passes optional inputs as kwargs, unconnected inputs are omitted entirely"
  - "Loop-based INPUT_TYPES construction for numbered optional inputs (image_1..image_9)"

requirements-completed: [OMNI-01, OMNI-02, OMNI-03]

# Metrics
duration: 5min
completed: 2026-04-03
---

# Phase 03 Plan 02: Omni Reference Summary

**Omni Reference node combining up to 9 images and 3 video URLs via base64 JPEG data URIs for multi-modal Seedance 2.0 video generation**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-03T13:44:39Z
- **Completed:** 2026-04-03T13:49:54Z
- **Tasks:** 2 (+ 1 auto-skipped checkpoint)
- **Files modified:** 7

## Accomplishments
- create_omni_video and create_and_wait_omni API functions supporting image_data_uris (list of base64 data URIs) and video_urls (list of URL strings)
- SeedanceOmniReference node with 9 optional IMAGE inputs (image_1..image_9) + 3 optional STRING video URL inputs (video_url_1..video_url_3) + prompt + generation params
- Each connected IMAGE tensor converted to base64 JPEG data URI using I2V pattern (np.clip + PIL + base64 encoding)
- Unconnected image/video slots silently ignored (None check for images, empty string check for video URLs)
- 24 new tests: 7 TestCreateOmniVideo + 2 TestCreateAndWaitOmni + 15 TestSeedanceOmniReference

## Task Commits

Each task was committed atomically:

1. **Task 0: API Verification checkpoint** - auto-skipped (verify-skip selected in auto-mode)
2. **Task 1: Add Omni API client functions and tests** - `7fc0797` (feat)
3. **Task 2: Add SeedanceOmniReference node with registration and tests** - `63ad21f` (feat)

## Files Created/Modified
- `api_client.py` - Added create_omni_video() and create_and_wait_omni() functions after create_and_wait_extend
- `nodes.py` - Added SeedanceOmniReference class with **kwargs pattern for 9+3 optional inputs
- `__init__.py` - Registered SeedanceOmniReference as "Seedance 2.0 Omni Reference"
- `tests/conftest.py` - Added mock_omni_response fixture
- `tests/test_api_client.py` - Added TestCreateOmniVideo (7 tests) and TestCreateAndWaitOmni (2 tests)
- `tests/test_nodes.py` - Added TestSeedanceOmniReference (15 tests)
- `tests/test_registration.py` - Updated expected_keys to include SeedanceOmniReference (6 nodes total)

## Decisions Made
- Skipped API verification per auto-mode -- using array of data URIs as "input" field and "video_urls" field in payload (hypothesis A from plan)
- Used **kwargs in generate() method because ComfyUI passes optional inputs as keyword args and unconnected optional IMAGE inputs are omitted entirely
- image_data_uris and video_urls are passed as None (not empty list) to API when nothing is connected, matching the plan specification

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 03 complete. All three generation modes (T2V, I2V, Extend) and Omni Reference are implemented
- 6 nodes registered: SeedanceApiKey, SeedanceTextToVideo, SeedanceImageToVideo, SeedanceSaveVideo, SeedanceExtendVideo, SeedanceOmniReference
- 115 tests passing across all modules
- Ready for Phase 04: GitHub publication and ComfyUI Manager installation

---
*Phase: 03-extend-omni-reference*
*Completed: 2026-04-03*

## Self-Check: PASSED

All 7 files verified present. Both task commits (7fc0797, 63ad21f) verified in git log.

---
phase: 03-extend-omni-reference
plan: 01
subsystem: api
tags: [seedance, video-extend, comfyui-node, aihubmix]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: api_client.py base functions, SeedanceTextToVideo node pattern
  - phase: 02-i2v-save
    provides: create_i2v_video pattern, create_and_wait_i2v orchestration pattern
provides:
  - create_extend_video API function in api_client.py
  - create_and_wait_extend orchestration function in api_client.py
  - SeedanceExtendVideo ComfyUI node class
  - "Seedance 2.0 Video Extend" node registration
  - 20 new tests (8 API client + 12 node)
affects: [03-02-PLAN, any future phase needing video extend workflow]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "request_id field in API payload for video extend (MuAPI-compatible hypothesis)"
    - "video_id as required STRING input for extend nodes"

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
  - "Skipped API verification (auto-mode) -- using MuAPI-compatible request_id payload format"
  - "video_id is required input (not optional) -- prevents accidental empty calls"
  - "Empty prompt allowed for extend -- user may want pure continuation without new direction"

patterns-established:
  - "Extend node follows identical pattern to T2V/I2V nodes: same RETURN_TYPES, RETURN_NAMES, CATEGORY, optional fields"
  - "create_extend_video uses request_id field to reference source video_id"

requirements-completed: [EXTD-01, EXTD-02, EXTD-03]

# Metrics
duration: 4min
completed: 2026-04-03
---

# Phase 03 Plan 01: Video Extend Summary

**Video Extend node with request_id-based API payload, enabling multi-shot video workflows by chaining video_id outputs between nodes**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-03T13:35:44Z
- **Completed:** 2026-04-03T13:40:35Z
- **Tasks:** 2 (Task 0 auto-approved checkpoint, Tasks 1-2 executed)
- **Files modified:** 7

## Accomplishments
- Added create_extend_video and create_and_wait_extend functions to api_client.py following existing I2V pattern
- Added SeedanceExtendVideo ComfyUI node with video_id (required STRING) + prompt (required STRING) + optional generation params
- Node validates both api_key and video_id before API call, with Chinese error for missing video_id
- Registered as "Seedance 2.0 Video Extend" in __init__.py
- 20 new tests all passing (6 TestCreateExtendVideo + 2 TestCreateAndWaitExtend + 12 TestSeedanceExtendVideo)
- All 91 total tests pass (existing Phase 1/2 tests unaffected)

## Task Commits

Each task was committed atomically:

1. **Task 0: API Verification checkpoint** - auto-approved (verify-skip selected)
2. **Task 1: Add Extend API client functions and tests** - `c9c45b0` (feat)
3. **Task 2: Add SeedanceExtendVideo node, registration, tests** - `2ef13bf` (feat)

## Files Created/Modified
- `api_client.py` - Added create_extend_video (request_id payload) and create_and_wait_extend orchestration
- `nodes.py` - Added SeedanceExtendVideo class with video_id + prompt inputs, api_key/video_id validation
- `__init__.py` - Registered SeedanceExtendVideo in both NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS
- `tests/conftest.py` - Added mock_extend_response fixture
- `tests/test_api_client.py` - Added TestCreateExtendVideo (6 tests) and TestCreateAndWaitExtend (2 tests)
- `tests/test_nodes.py` - Added TestSeedanceExtendVideo (12 tests)
- `tests/test_registration.py` - Updated expected_keys to include SeedanceExtendVideo

## Decisions Made
- **Skipped API verification (auto-mode):** Using MuAPI-compatible hypothesis with `request_id` field in payload posted to `/v1/videos`. The actual API format will be validated during manual testing.
- **video_id as required input:** Prevents accidental empty calls; Chinese error message guides user to wire video_id output from generation nodes.
- **Empty prompt allowed:** User may want pure video continuation without specifying a new direction.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all tests passed on first run, no build issues.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Video Extend node complete, ready for manual API verification
- Phase 03 Plan 02 (Omni Reference) can proceed using the same node pattern
- Blocker concern: AIHubMix actual extend API format still unverified -- may need payload adjustments post-testing

## Self-Check: PASSED

- All 7 modified/created files verified present on disk
- Commit c9c45b0 (Task 1) verified in git log
- Commit 2ef13bf (Task 2) verified in git log
- 91 total tests passing (71 existing + 20 new)

---
*Phase: 03-extend-omni-reference*
*Completed: 2026-04-03*

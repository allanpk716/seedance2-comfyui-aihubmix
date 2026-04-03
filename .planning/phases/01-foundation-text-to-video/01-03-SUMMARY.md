---
phase: 01-foundation-text-to-video
plan: 03
subsystem: nodes
tags: [comfyui, custom-nodes, api-key, text-to-video, seedance]

# Dependency graph
requires:
  - phase: 01-foundation-text-to-video/01
    provides: "__init__.py with NODE_CLASS_MAPPINGS importing from nodes.py"
  - phase: 01-foundation-text-to-video/02
    provides: "api_client.create_and_wait function for video generation"
provides:
  - "SeedanceApiKey node class - STRING passthrough for API key wiring"
  - "SeedanceTextToVideo node class - full T2V generation with all parameters"
  - "18 unit tests covering all node behaviors"
affects: [phase-02-video-download, phase-03-image-to-video]

# Tech tracking
tech-stack:
  added: []
  patterns: [comfyui-node-class, optional-api-key-field, enum-input-types]

key-files:
  created:
    - tests/test_nodes.py
  modified:
    - nodes.py

key-decisions:
  - "Mock patch target must be seedance_comfyui.nodes.create_and_wait (not api_client module) because nodes.py imports the function into its own namespace"
  - "RETURN_TYPES is (STRING, STRING) for video_url + video_id only -- no IMAGE output per D-01 override"
  - "Optional api_key field with empty string default allows both wiring and direct entry per D-06"

patterns-established:
  - "ComfyUI node class: CATEGORY, INPUT_TYPES classmethod, RETURN_TYPES, RETURN_NAMES, FUNCTION, OUTPUT_NODE attributes"
  - "Optional parameters via INPUT_TYPES optional dict with sensible defaults"
  - "ValueError for missing required runtime values (API key) with actionable guidance"

requirements-completed: [KEYM-01, KEYM-02, KEYM-03, T2V-01, T2V-02, T2V-03, T2V-04]

# Metrics
duration: 3min
completed: 2026-04-03
---

# Phase 1 Plan 03: ComfyUI Node Classes Summary

**SeedanceApiKey passthrough node and SeedanceTextToVideo generation node with prompt, duration (4-15s), resolution (1080p/720p/480p), and ratio (6 options) parameters**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-03T05:48:34Z
- **Completed:** 2026-04-03T05:51:41Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 2

## Accomplishments
- SeedanceApiKey node accepts STRING input and returns it unchanged for wiring to generation nodes
- SeedanceTextToVideo node with full parameter support: prompt (required), api_key (optional), duration, resolution, ratio
- Missing API key raises ValueError with aihubmix.com guidance per KEYM-03
- All 36 tests pass across 3 test files (registration: 4, API client: 14, nodes: 18)

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Node tests (failing)** - `d9606c2` (test)
2. **Task 1 GREEN: Node implementation** - `0f49cb6` (feat)

_Note: TDD task had test-first commit then implementation commit_

## Files Created/Modified
- `tests/test_nodes.py` - 18 unit tests for SeedanceApiKey (6 tests) and SeedanceTextToVideo (12 tests) node classes
- `nodes.py` - Full implementation of SeedanceApiKey and SeedanceTextToVideo replacing Plan 01 stubs

## Decisions Made
- Mock patch path uses `seedance_comfyui.nodes.create_and_wait` because `nodes.py` imports the function into its own namespace via `from .api_client import create_and_wait`
- Followed plan exactly for node structure: CATEGORY, INPUT_TYPES, RETURN_TYPES, RETURN_NAMES, FUNCTION, OUTPUT_NODE attributes

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed mock patch target path in tests**
- **Found during:** Task 1 (TDD GREEN phase)
- **Issue:** Tests patched `seedance_comfyui.api_client.create_and_wait` but the import in nodes.py binds the function in the nodes module namespace, so the mock was not intercepting the call
- **Fix:** Changed patch target to `seedance_comfyui.nodes.create_and_wait` where the name is actually looked up at call time
- **Files modified:** tests/test_nodes.py
- **Verification:** All 18 tests pass, create_and_wait mock correctly intercepts calls
- **Committed in:** 0f49cb6 (Task 1 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Minor test fix. Implementation matched plan exactly.

## Issues Encountered
None - implementation followed plan specification precisely.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Node classes fully implemented, Phase 1 foundation complete
- Phase 2 can build video download/save nodes that connect to SeedanceTextToVideo outputs (video_url, video_id)
- Phase 3 image-to-video nodes will follow the same pattern as SeedanceTextToVideo

---
*Phase: 01-foundation-text-to-video*
*Completed: 2026-04-03*

## Self-Check: PASSED

- FOUND: nodes.py
- FOUND: tests/test_nodes.py
- FOUND: .planning/phases/01-foundation-text-to-video/01-03-SUMMARY.md
- FOUND: d9606c2 (RED commit)
- FOUND: 0f49cb6 (GREEN commit)

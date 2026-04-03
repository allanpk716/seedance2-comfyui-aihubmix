---
phase: 3
slug: extend-omni-reference
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | none — existing discovery in tests/ directory |
| **Quick run command** | `python -m pytest tests/test_nodes.py tests/test_api_client.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_nodes.py tests/test_api_client.py -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | EXTD-01 | unit | `python -m pytest tests/test_api_client.py::TestCreateExtendVideo -x -q` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | EXTD-01, EXTD-02 | unit | `python -m pytest tests/test_nodes.py::TestSeedanceExtendVideo -x -q` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | EXTD-03 | unit | `python -m pytest tests/test_nodes.py::TestSeedanceExtendVideo::test_extend_size_options -x -q` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | OMNI-01 | unit | `python -m pytest tests/test_api_client.py::TestCreateOmniVideo -x -q` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 2 | OMNI-01, OMNI-02 | unit | `python -m pytest tests/test_nodes.py::TestSeedanceOmniReference -x -q` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 2 | OMNI-03 | unit | `python -m pytest tests/test_nodes.py::TestSeedanceOmniReference::test_omni_return_types -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_api_client.py` — add TestCreateExtendVideo, TestCreateOmniVideo test classes
- [ ] `tests/test_nodes.py` — add TestSeedanceExtendVideo, TestSeedanceOmniReference test classes
- [ ] `tests/conftest.py` — add mock_extend_response, mock_omni_response fixtures

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Extend node API call reaches AIHubMix and returns extended video | EXTD-01 | Requires real API key and prior video_id | Run `python seedance_video.py --extend --video-id <ID>` with real API key |
| Omni node API call reaches AIHubMix with multi-modal payload | OMNI-01 | Requires real API key and test images | Run `python seedance_video.py --omni --images img1.jpg` with real API key |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

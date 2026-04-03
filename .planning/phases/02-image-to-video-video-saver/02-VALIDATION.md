---
phase: 2
slug: image-to-video-video-saver
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | none — auto-discovery |
| **Quick run command** | `python -m pytest tests/ -x --tb=short -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x --tb=short -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | I2V-01, I2V-02 | unit | `python -m pytest tests/test_api_client.py::test_create_i2v_video -x` | ✅ conftest.py | ⬜ pending |
| 02-01-02 | 01 | 1 | I2V-01, I2V-02, I2V-03, I2V-04 | unit | `python -m pytest tests/test_nodes.py::TestSeedanceImageToVideo -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | VSAV-01, VSAV-02, VSAV-03, VSAV-04 | unit | `python -m pytest tests/test_nodes.py::TestSeedanceSaveVideo -x` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 1 | I2V-01..04, VSAV-01..04 | unit | `python -m pytest tests/test_registration.py -x` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pip install opencv-python>=4.7` — needed for Save Video frame extraction tests
- [ ] `tests/conftest.py` — add I2V-specific fixtures (mock_i2v_response, sample_image_tensor)
- [ ] `tests/test_nodes.py` — add `TestSeedanceImageToVideo` stubs
- [ ] `tests/test_nodes.py` — add `TestSeedanceSaveVideo` stubs
- [ ] `folder_paths` mock — ComfyUI module not available outside runtime

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ComfyUI canvas video preview | VSAV-03 | Requires running ComfyUI instance | Run workflow with T2V -> Save Video, verify .mp4 preview appears in canvas |
| I2V end-to-end with real API | I2V-01 | Requires valid AIHubMix API key + credits | Wire Image -> I2V -> Save Video, verify video generated from reference image |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

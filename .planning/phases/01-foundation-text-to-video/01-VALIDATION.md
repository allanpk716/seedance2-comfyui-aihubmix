---
phase: 1
slug: foundation-text-to-video
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | PFND-01 | unit | `pytest tests/test_registration.py::test_node_class_mappings -x` | W0 | pending |
| 01-01-02 | 01 | 1 | PFND-02 | unit | `pytest tests/test_registration.py::test_node_categories -x` | W0 | pending |
| 01-01-03 | 01 | 1 | PFND-03 | unit | `pytest tests/test_registration.py::test_requirements -x` | W0 | pending |
| 01-02-01 | 02 | 1 | APIC-01 | unit | `pytest tests/test_api_client.py -x` | W0 | pending |
| 01-02-02 | 02 | 1 | APIC-02 | unit | `pytest tests/test_api_client.py::test_auth_header -x` | W0 | pending |
| 01-02-03 | 02 | 1 | APIC-03 | unit | `pytest tests/test_api_client.py::test_polling -x` | W0 | pending |
| 01-02-04 | 02 | 1 | APIC-04 | unit | `pytest tests/test_api_client.py::test_error_handling -x` | W0 | pending |
| 01-02-05 | 02 | 1 | APIC-05 | unit | `pytest tests/test_api_client.py::test_model_id -x` | W0 | pending |
| 01-03-01 | 03 | 2 | KEYM-01 | unit | `pytest tests/test_nodes.py::test_api_key_passthrough -x` | W0 | pending |
| 01-03-02 | 03 | 2 | KEYM-02 | unit | `pytest tests/test_nodes.py::test_t2v_optional_key -x` | W0 | pending |
| 01-03-03 | 03 | 2 | KEYM-03 | unit | `pytest tests/test_nodes.py::test_missing_key_error -x` | W0 | pending |
| 01-03-04 | 03 | 2 | T2V-01 | unit | `pytest tests/test_nodes.py::test_t2v_prompt -x` | W0 | pending |
| 01-03-05 | 03 | 2 | T2V-02 | unit | `pytest tests/test_nodes.py::test_t2v_size_options -x` | W0 | pending |
| 01-03-06 | 03 | 2 | T2V-03 | unit | `pytest tests/test_nodes.py::test_t2v_duration -x` | W0 | pending |
| 01-03-07 | 03 | 2 | T2V-04 | unit | `pytest tests/test_nodes.py::test_t2v_outputs -x` | W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_registration.py` — stubs for PFND-01, PFND-02, PFND-03
- [ ] `tests/test_api_client.py` — stubs for APIC-01 through APIC-05
- [ ] `tests/test_nodes.py` — stubs for KEYM-01 through KEYM-03, T2V-01 through T2V-04
- [ ] `tests/conftest.py` — shared fixtures (mock API responses, sample video data)
- [ ] `pytest` + `pytest-mock` install — if not present in environment

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Plugin appears in ComfyUI node menu | PFND-01, PFND-02 | Requires running ComfyUI with plugin installed | Install plugin in ComfyUI custom_nodes/, restart, check node menu for "Seedance 2.0" category |
| T2V end-to-end with real API key | T2V-01 | Requires real API key and network access | Wire API Key node to T2V node, enter prompt, verify video URL returned |
| Error messages in ComfyUI console | APIC-04 | Requires ComfyUI runtime | Test with invalid key, verify Chinese error message appears in console |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

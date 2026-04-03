# Seedance 2.0 ComfyUI Plugin (AIHubMix)

## What This Is

A ComfyUI custom node plugin that integrates ByteDance's Seedance 2.0 video generation model via the AIHubMix API service. Based on the open-source [seedance2-comfyui](https://github.com/Anil-matcha/seedance2-comfyui) project, adapted to use AIHubMix as the API provider instead of muapi.ai. Published as a standalone GitHub repository for installation via ComfyUI Manager.

## Core Value

Users can generate Seedance 2.0 AI videos directly inside ComfyUI by entering their AIHubMix API key, without needing muapi.ai or any other service.

## Requirements

### Validated

- Text-to-Video: User provides a text prompt and generates a video via AIHubMix API (Validated in Phase 1: Foundation + Text-to-Video)
- API Key Node: Dedicated node for entering AIHubMix API key, passed to generation nodes (Validated in Phase 1)
- ComfyUI Manager Compatible: Proper `__init__.py` registration for ComfyUI discovery (Validated in Phase 1)

### Active

- [ ] Video Extend: User can extend a previously generated video using the request ID
- [ ] Omni Reference: User can combine multiple images, video URLs, and audio URLs for generation
- [ ] GitHub Repository: Published on GitHub with README for ComfyUI Manager installation

### Validated (Phase 2)

- Image-to-Video: User provides reference image + prompt to generate video via AIHubMix I2V endpoint (Validated in Phase 2: Image-to-Video + Video Saver)
- Video Save/Download: SeedanceSaveVideo OUTPUT_NODE downloads video, extracts frames as IMAGE tensors, saves first frame PNG, returns UI preview (Validated in Phase 2)

### Out of Scope

- Consistent Character workflow — complex multi-step pipeline, defer to v2
- Local model inference — cloud API only
- muapi.ai backward compatibility — clean switch to AIHubMix only
- Environment variable / config file API key — node input only for v1 simplicity

## Context

- **Reference project:** [Anil-matcha/seedance2-comfyui](https://github.com/Anil-matcha/seedance2-comfyui) uses muapi.ai as the API provider
- **Target API:** AIHubMix (`https://aihubmix.com/v1`) uses OpenAI-compatible video API format
- **API differences:** AIHubMix uses `Authorization: Bearer` header (vs muapi's `x-api-key`), RESTful `/videos` endpoints (vs `/seedance-v2.0-*`), and supports base64/URL/data URI for image input directly (no separate upload step needed)
- **Model ID:** `doubao-seedance-2-0-260128`
- **Test script exists:** `seedance_video.py` validates the AIHubMix API works correctly with T2V and I2V flows

### API Endpoint Mapping (muapi.ai → AIHubMix)

| Function | muapi.ai | AIHubMix |
|----------|----------|----------|
| Auth header | `x-api-key` | `Authorization: Bearer` |
| Create video | POST `/api/v1/seedance-v2.0-t2v` | POST `/v1/videos` |
| Poll status | GET `/api/v1/predictions/{id}/result` | GET `/v1/videos/{id}` |
| Download | URL from result | GET `/v1/videos/{id}/content` |
| Image upload | POST `/api/v1/upload_file` (separate step) | Inline base64/URL in `input` field |

### AIHubMix API Details

- **Supported resolutions:** 480p, 720p, 1080p with various aspect ratios
- **Duration:** 4-15 seconds
- **Image input:** Supports URL, local file (base64 data URI), data URI directly
- **Response format:** Returns video ID on creation, poll for completion status with progress %

## Constraints

- **Tech Stack:** Python 3, ComfyUI custom node API, `requests` library
- **API Format:** Must follow AIHubMix OpenAI-compatible video API format
- **Security:** API keys must never be hardcoded or committed to git
- **ComfyUI Compatibility:** Must follow standard custom node structure (`NODE_CLASS_MAPPINGS`, `NODE_DISPLAY_NAME_MAPPINGS` in `__init__.py`)
- **Dependencies:** Minimal — only `requests`, `opencv-python` (for frame extraction), standard library

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Fork and modify seedance2-comfyui | API 层虽不同但 ComfyUI 节点框架可直接复用；比从零实现更快更稳 | — Pending |
| Use AIHubMix API exclusively | User's service provider; clean single-provider implementation | — Pending |
| API key via node input only | Simplest UX for v1; no config file management needed | — Pending |
| Base reference project structure | Proven ComfyUI node pattern; easy to adapt | — Pending |
| Image input via base64/URL inline | AIHubMix supports direct inline input; no separate upload endpoint needed | — Pending |
| Publish to GitHub for ComfyUI Manager | User wants to share and install via ComfyUI Manager | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-03 after Phase 2 completion*

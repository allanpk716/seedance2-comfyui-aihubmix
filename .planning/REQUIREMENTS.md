# Requirements: Seedance 2.0 ComfyUI Plugin (AIHubMix)

**Defined:** 2026-04-03
**Core Value:** Users can generate Seedance 2.0 AI videos directly inside ComfyUI using their AIHubMix API key

## v1 Requirements

**Implementation approach:** Fork [seedance2-comfyui](https://github.com/Anil-matcha/seedance2-comfyui) and modify API layer for AIHubMix. Reuse ComfyUI node framework, tensor conversion, VideoSaver. Remove Character/ConsistentVideo nodes.

### Plugin Foundation

- [x] **PFND-01**: Plugin registers with ComfyUI via `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS` in `__init__.py`
- [x] **PFND-02**: All nodes appear under "Seedance 2.0" category in ComfyUI node menu
- [x] **PFND-03**: `requirements.txt` lists all dependencies (requests, opencv-python, Pillow)
- [ ] **PFND-04**: Plugin is installable via ComfyUI Manager "Install via Git URL"

### API Client

- [x] **APIC-01**: API client module handles all AIHubMix HTTP communication (`POST /v1/videos`, `GET /v1/videos/{id}`, `GET /v1/videos/{id}/content`)
- [x] **APIC-02**: Authentication uses `Authorization: Bearer {key}` header
- [x] **APIC-03**: API client polls for video completion every 5 seconds with progress logging to console
- [x] **APIC-04**: Error handling provides clear messages for 401 (auth), 402 (credits), 429 (rate limit), network failures
- [x] **APIC-05**: Model identifier `doubao-seedance-2-0-260128` is used for all requests

### API Key Management

- [x] **KEYM-01**: Dedicated API Key node accepts STRING input and passes to generation nodes
- [x] **KEYM-02**: Each generation node has optional `api_key` field as fallback when not wired from Key node
- [x] **KEYM-03**: Missing API key produces clear error message with instructions

### Text-to-Video

- [x] **T2V-01**: User provides text prompt to generate video via AIHubMix T2V
- [x] **T2V-02**: User can select resolution (480p, 720p, 1080p) and aspect ratio (16:9, 9:16, 4:3, 3:4, 1:1, 21:9)
- [x] **T2V-03**: User can set video duration (4-15 seconds, default 5)
- [x] **T2V-04**: Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING)

### Image-to-Video

- [ ] **I2V-01**: User provides IMAGE tensor + prompt to generate video with reference image
- [ ] **I2V-02**: Image is converted from ComfyUI tensor (B,H,W,C float32) to base64 JPEG data URI for API
- [ ] **I2V-03**: Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING)
- [ ] **I2V-04**: User can select resolution, aspect ratio, and duration same as T2V

### Video Extend

- [ ] **EXTD-01**: User provides video_id from a prior generation + optional continuation prompt
- [ ] **EXTD-02**: Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING)
- [ ] **EXTD-03**: User can select resolution, aspect ratio, and duration same as T2V

### Omni Reference

- [ ] **OMNI-01**: User can combine multiple images (up to 9) + video URLs (up to 3) + prompt for multi-modal generation
- [ ] **OMNI-02**: Each image input is converted from ComfyUI tensor to base64 data URI
- [ ] **OMNI-03**: Node outputs video_url (STRING), first_frame (IMAGE), video_id (STRING)

### Video Save & Preview

- [ ] **VSAV-01**: Save Video node downloads generated video from URL to ComfyUI output directory
- [ ] **VSAV-02**: Node extracts frames and returns as ComfyUI IMAGE tensor with frame_load_cap to prevent OOM
- [ ] **VSAV-03**: Video preview displays in ComfyUI UI canvas (OUTPUT_NODE with gifs preview)
- [ ] **VSAV-04**: User can configure filename prefix and save subfolder

## v2 Requirements

### Consistent Character

- **CHAR-01**: Character Sheet node generates character sheet from 1-3 reference photos
- **CHAR-02**: Consistent Character Video node maintains character identity from character sheet

### Advanced Features

- **ADVN-01**: Configurable poll interval for advanced users
- **ADVN-02**: Retry with exponential backoff for transient API failures
- **ADVN-03**: Batch generation support via ComfyUI queue

## Out of Scope

| Feature | Reason |
|---------|--------|
| Local model inference | Cloud API only, not the plugin's purpose |
| Multi-provider support (muapi.ai, fal.ai, etc.) | Single clean AIHubMix implementation |
| Environment variable / config file API key | Node input only for v1 simplicity |
| Custom JavaScript UI widgets | Standard ComfyUI input types sufficient |
| Video-to-video / video editing | AIHubMix API surface unclear, complex workflow |
| Audio generation controls | Let model auto-generate, don't expose audio params |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PFND-01 | Phase 1 | Complete |
| PFND-02 | Phase 1 | Complete |
| PFND-03 | Phase 1 | Complete |
| PFND-04 | Phase 4 | Pending |
| APIC-01 | Phase 1 | Complete |
| APIC-02 | Phase 1 | Complete |
| APIC-03 | Phase 1 | Complete |
| APIC-04 | Phase 1 | Complete |
| APIC-05 | Phase 1 | Complete |
| KEYM-01 | Phase 1 | Complete |
| KEYM-02 | Phase 1 | Complete |
| KEYM-03 | Phase 1 | Complete |
| T2V-01 | Phase 1 | Complete |
| T2V-02 | Phase 1 | Complete |
| T2V-03 | Phase 1 | Complete |
| T2V-04 | Phase 1 | Complete |
| I2V-01 | Phase 2 | Pending |
| I2V-02 | Phase 2 | Pending |
| I2V-03 | Phase 2 | Pending |
| I2V-04 | Phase 2 | Pending |
| EXTD-01 | Phase 3 | Pending |
| EXTD-02 | Phase 3 | Pending |
| EXTD-03 | Phase 3 | Pending |
| OMNI-01 | Phase 3 | Pending |
| OMNI-02 | Phase 3 | Pending |
| OMNI-03 | Phase 3 | Pending |
| VSAV-01 | Phase 2 | Pending |
| VSAV-02 | Phase 2 | Pending |
| VSAV-03 | Phase 2 | Pending |
| VSAV-04 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0

---
*Requirements defined: 2026-04-03*
*Last updated: 2026-04-03 after initial definition*

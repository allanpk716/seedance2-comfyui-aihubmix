# Roadmap: Seedance 2.0 ComfyUI Plugin (AIHubMix)

## Overview

Build a ComfyUI custom node plugin that integrates ByteDance's Seedance 2.0 video generation via the AIHubMix API. Start by forking the reference project, replacing the API layer, and validating the simplest flow (text-to-video). Then add image input and video saving. Then complete the feature set with video extension and omni reference. Finally, publish to GitHub for ComfyUI Manager installation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation + Text-to-Video** - Plugin scaffolding, API client, key management, and T2V node working end-to-end
- [ ] **Phase 2: Image-to-Video + Video Saver** - I2V node with image tensor conversion, and video download/preview node
- [ ] **Phase 3: Extend + Omni Reference** - Video extend and multi-modal omni reference nodes
- [ ] **Phase 4: Publish** - GitHub repository setup, README, ComfyUI Manager compatibility verification

## Phase Details

### Phase 1: Foundation + Text-to-Video
**Goal**: Users can enter their AIHubMix API key and generate a video from a text prompt inside ComfyUI
**Depends on**: Nothing (first phase)
**Requirements**: PFND-01, PFND-02, PFND-03, APIC-01, APIC-02, APIC-03, APIC-04, APIC-05, KEYM-01, KEYM-02, KEYM-03, T2V-01, T2V-02, T2V-03, T2V-04
**Success Criteria** (what must be TRUE):
  1. Plugin appears in ComfyUI node menu under "Seedance 2.0" category with all Phase 1 nodes listed
  2. User can enter an API key via the SeedanceApiKey node and it is passed to the T2V node via connection
  3. User can type a text prompt, select resolution/aspect ratio/duration, and trigger video generation that completes with a video URL returned
  4. Invalid or missing API key produces a clear error message telling the user what to do
  5. API errors (auth failure, insufficient credits, rate limit, network) show human-readable messages in the ComfyUI console
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md -- Plugin scaffold with __init__.py registration, requirements.txt, test infrastructure
- [x] 01-02-PLAN.md -- AIHubMix API client module with create, poll, error handling (mocked tests)
- [x] 01-03-PLAN.md -- API Key node and Text-to-Video node with all parameters (TDD)

### Phase 2: Image-to-Video + Video Saver
**Goal**: Users can generate videos from reference images and download/preview the results as ComfyUI tensors
**Depends on**: Phase 1
**Requirements**: I2V-01, I2V-02, I2V-03, I2V-04, VSAV-01, VSAV-02, VSAV-03, VSAV-04
**Success Criteria** (what must be TRUE):
  1. User can wire a ComfyUI IMAGE tensor into the I2V node along with a prompt and generate a video from that reference image
  2. Image tensor is correctly converted from ComfyUI format (B,H,W,C float32) to base64 JPEG for the API without distortion
  3. User can download a generated video via the Save Video node and the file appears in the ComfyUI output directory
  4. Save Video node extracts frames and returns them as a ComfyUI IMAGE tensor that can be previewed or passed to downstream nodes
  5. User can configure filename prefix and save subfolder for organized output
**Plans**: TBD

Plans:
- [ ] 02-01: Build Image-to-Video node with tensor-to-base64 conversion
- [ ] 02-02: Build Video Save node with download, frame extraction, and preview

### Phase 3: Extend + Omni Reference
**Goal**: Users can extend previously generated videos and combine multiple images/videos into multi-modal generation requests
**Depends on**: Phase 2
**Requirements**: EXTD-01, EXTD-02, EXTD-03, OMNI-01, OMNI-02, OMNI-03
**Success Criteria** (what must be TRUE):
  1. User can take a video_id output from a prior generation and wire it into the Extend node to continue the video with an optional continuation prompt
  2. Extend node supports the same resolution, aspect ratio, and duration controls as T2V
  3. User can wire up to 9 images and up to 3 video URLs into the Omni Reference node along with a prompt and generate a multi-modal video
  4. Each image input to Omni Reference is correctly converted from ComfyUI tensor to base64 data URI
  5. Both Extend and Omni Reference nodes output video_url, first_frame (IMAGE), and video_id like the other generation nodes
**Plans**: TBD

Plans:
- [ ] 03-01: Build Video Extend node
- [ ] 03-02: Build Omni Reference node with multi-image and video URL inputs

### Phase 4: Publish
**Goal**: Users can install the plugin via ComfyUI Manager and get started from a README
**Depends on**: Phase 3
**Requirements**: PFND-04
**Success Criteria** (what must be TRUE):
  1. Plugin repository is publicly accessible on GitHub with a README showing installation instructions
  2. User can install the plugin via ComfyUI Manager "Install via Git URL" and all nodes appear after ComfyUI restart
  3. README includes example workflow description showing how to use the basic T2V and I2V nodes
**Plans**: TBD

Plans:
- [ ] 04-01: Finalize GitHub repo, write README, verify ComfyUI Manager installation

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation + Text-to-Video | 0/3 | Planning complete | - |
| 2. Image-to-Video + Video Saver | 0/2 | Not started | - |
| 3. Extend + Omni Reference | 0/2 | Not started | - |
| 4. Publish | 0/1 | Not started | - |

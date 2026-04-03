# Research Summary: Seedance 2.0 ComfyUI Plugin (AIHubMix)

**Domain:** ComfyUI Custom Node Plugin for AI Video Generation
**Researched:** 2026-04-03
**Overall confidence:** HIGH

## Executive Summary

This project is a greenfield ComfyUI custom node plugin that integrates ByteDance's Seedance 2.0 video generation model through the AIHubMix cloud API. The plugin follows a well-established pattern in the ComfyUI ecosystem: synchronous Python node classes that call a REST API, poll for completion, and return results as standard ComfyUI tensors and strings.

The technology stack is deliberately minimal -- `requests` for HTTP, `opencv-python` for video frame extraction, and `Pillow` for image conversion. No exotic dependencies, no async framework, no custom JavaScript widgets. This matches what every successful API-backed ComfyUI plugin uses (Kling, Runway, Sora nodes all follow this pattern).

The architecture separates concerns cleanly into four files: API client module, generation node classes, video saver node, and registration. The key differentiator from the reference project (which uses muapi.ai) is that AIHubMix accepts inline base64 image data in the request body, eliminating the separate upload step and simplifying the I2V and Omni Reference flows.

The most critical pitfall is the existing test script containing a hardcoded API key that must be excluded from git before any public push. The second most critical is getting the ComfyUI IMAGE tensor format right -- it uses `[B, H, W, C]` float32, not PyTorch's standard `[B, C, H, W]`.

## Key Findings

**Stack:** Python >= 3.8 + requests >= 2.28 + opencv-python >= 4.7 + Pillow >= 9.0 + PyTorch (already in ComfyUI). Synchronous execution only. No async libraries needed or beneficial.

**Architecture:** Four-file structure (api client, generation nodes, video saver, registration). Module-level API functions (not a class). Six nodes total: ApiKey, T2V, I2V, Extend, Omni Reference, VideoSaver. All under `CATEGORY = "Seedance 2.0"`.

**Critical pitfall:** The test script `seedance_video.py` has a hardcoded API key. This must be in `.gitignore` before the first commit. After that, the tensor format pitfall (NHWC not NCHW) is the second most likely to cause a rewrite.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Phase 1: Foundation + Text-to-Video** - Build the minimum that produces a visible result
   - Addresses: API Key Node, Text-to-Video, ComfyUI Manager compatible packaging
   - Avoids: Tensor format pitfall (focus on string-only flow first, no IMAGE output yet)
   - Validates: AIHubMix API integration works from inside ComfyUI

2. **Phase 2: Image-to-Video + Video Saver** - Add the most valuable secondary features
   - Addresses: I2V (with image tensor conversion), VideoSaver (download + frame extraction + preview)
   - Avoids: OOM pitfall (implement frame_load_cap from the start in VideoSaver)
   - Validates: IMAGE tensor pipeline works correctly (NHWC, float32, RGB)

3. **Phase 3: Extend + Omni Reference** - Complete the feature set
   - Addresses: Video Extend, Omni Reference (multi-modal input)
   - Avoids: API key exposure (already handled in Phase 1 setup)
   - Validates: All Seedance 2.0 capabilities are accessible through ComfyUI

4. **Phase 4: Polish + Publish** - GitHub distribution and documentation
   - Addresses: README, example workflows, ComfyUI Manager listing
   - Avoids: ComfyUI Manager incompatibility (test clone + restart)
   - Validates: Users can install via ComfyUI Manager git URL

**Phase ordering rationale:**
- Phase 1 before Phase 2 because T2V is the simplest flow (no IMAGE tensor conversion needed) and validates the API client independently.
- Phase 2 before Phase 3 because VideoSaver is needed to see results from any node, and I2V is the second most common use case.
- Phase 3 last because Extend and Omni are power-user features that depend on the core flow working first.
- Phase 4 after all features because documentation should reflect the final state.

**Research flags for phases:**
- Phase 2: Needs deeper research into the exact AIHubMix video download response format (is it a redirect or direct bytes?)
- Phase 3: Needs verification that AIHubMix supports the Omni Reference payload format (multi-image + video + audio in single request)
- Phase 3: Needs verification of the exact Video Extend API payload structure for AIHubMix

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All libraries are proven in the ComfyUI ecosystem. The test script validates the API interaction pattern. Official docs confirm tensor format and node structure. |
| Features | HIGH | Based on reference project source code, official API docs, and established ComfyUI node patterns. 6 nodes cover all v1 requirements. |
| Architecture | HIGH | Standard ComfyUI custom node pattern. Separation of concerns is straightforward. File structure follows established conventions. |
| Pitfalls | HIGH | Critical pitfalls identified with specific prevention steps. API key exposure is an immediate action item. Tensor format is well-documented by ComfyUI. |

## Gaps to Address

- **AIHubMix Extend API payload:** The exact request body structure for video extension needs verification during Phase 3 implementation. The test script only covers T2V and I2V.
- **AIHubMix Omni Reference support:** Not confirmed whether AIHubMix supports the multi-modal input format (multiple images + video URLs + audio URLs in a single request). This needs a manual API test during Phase 3.
- **AIHubMix video download format:** Unclear whether `GET /v1/videos/{id}/content` returns a redirect (302) or direct bytes (200). The test script uses streaming download, which handles both.
- **URL expiration:** The TTL for AIHubMix video download URLs is not documented. Users should be advised to save videos immediately.
- **Windows-specific testing:** The project is being developed on Windows. Cross-platform path handling should use `pathlib.Path` throughout, but actual Linux/macOS testing is recommended before publishing.

<!-- GSD:project-start source:PROJECT.md -->
## Project

**Seedance 2.0 ComfyUI Plugin (AIHubMix)**

A ComfyUI custom node plugin that integrates ByteDance's Seedance 2.0 video generation model via the AIHubMix API service. Based on the open-source [seedance2-comfyui](https://github.com/Anil-matcha/seedance2-comfyui) project, adapted to use AIHubMix as the API provider instead of muapi.ai. Published as a standalone GitHub repository for installation via ComfyUI Manager.

**Core Value:** Users can generate Seedance 2.0 AI videos directly inside ComfyUI by entering their AIHubMix API key, without needing muapi.ai or any other service.

### Constraints

- **Tech Stack:** Python 3, ComfyUI custom node API, `requests` library
- **API Format:** Must follow AIHubMix OpenAI-compatible video API format
- **Security:** API keys must never be hardcoded or committed to git
- **ComfyUI Compatibility:** Must follow standard custom node structure (`NODE_CLASS_MAPPINGS`, `NODE_DISPLAY_NAME_MAPPINGS` in `__init__.py`)
- **Dependencies:** Minimal — only `requests`, `opencv-python` (for frame extraction), standard library
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | >= 3.8 | Runtime | ComfyUI minimum requirement. Use 3.10+ for `str \| None` type hints and match expressions if desired. |
| ComfyUI Custom Node API | Current | Plugin framework | ComfyUI loads nodes from `custom_nodes/` at startup via `NODE_CLASS_MAPPINGS` in `__init__.py`. No pip package needed -- just the right file structure. |
| PyTorch | >= 2.0 | Tensor handling | Already installed with ComfyUI. Required for IMAGE tensor format `[B, H, W, C]` float32 in `[0.0, 1.0]`. Do not pin or install separately. |
### HTTP Client
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **requests** | >= 2.28 | All API communication (create, poll, download) | Synchronous-only is correct here. ComfyUI node execution is inherently synchronous -- `run()` blocks until it returns. `requests` is the standard in the ComfyUI ecosystem, simplest API, and already proven with the existing `seedance_video.py` test script. |
### Video & Image Processing
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **opencv-python** | >= 4.7 | Video download to frames, frame extraction, BGR->RGB conversion | Already widely available in ComfyUI environments (most image nodes depend on it). Supports variable frame rate video. The 2x speed advantage of decord is negligible for 4-15 second videos. |
| **Pillow (PIL)** | >= 9.0 | Tensor-to-image conversion for API upload | Needed to convert ComfyUI IMAGE tensors to JPEG bytes for base64 encoding. Already in ComfyUI's dependency tree. |
| **numpy** | >= 1.23 | Array manipulation between torch tensors and image formats | Already installed with PyTorch. Used for dtype conversion (`float32 -> uint8`) and array operations in the image pipeline. |
### Packaging
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **requirements.txt** | N/A | Dependency declaration | ComfyUI Manager runs `pip install -r requirements.txt` after cloning. This is the standard installation mechanism. |
| **git + GitHub** | N/A | Distribution | ComfyUI Manager installs via `git clone` from a GitHub URL. The repo must have `__init__.py` with `NODE_CLASS_MAPPINGS` at its root. |
### Standard Library (No Install Needed)
| Module | Purpose |
|--------|---------|
| `base64` | Encode images to base64 data URIs for AIHubMix inline input |
| `io.BytesIO` | In-memory bytes buffer for PIL image encoding |
| `time` | `time.sleep()` for polling loop between status checks |
| `os` | File path handling, output directory creation |
| `json` | Response parsing (handled by `requests.json()` but useful for debugging) |
## Alternatives Considered (and Rejected)
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| HTTP Client | **requests** (sync) | httpx (sync+async) | httpx offers async and HTTP/2 but ComfyUI node execution is synchronous. Adding httpx gains nothing while introducing a less common dependency in the ComfyUI ecosystem. requests is already proven with the test script. |
| HTTP Client | **requests** (sync) | aiohttp (async-only) | aiohttp requires an event loop. ComfyUI's execution engine is synchronous. Using asyncio inside a sync `run()` method requires `asyncio.run()` which adds complexity and can conflict with ComfyUI's own event handling. No throughput benefit since ComfyUI executes nodes serially per prompt. |
| Video Decoding | **opencv-python** | decord (VideoReader) | decord is ~2x faster for frame extraction with hardware acceleration, but: (1) it is an extra dependency not commonly in ComfyUI environments, (2) the speed difference is negligible for 4-15 second videos (tens of milliseconds vs hundreds), (3) opencv handles variable frame rate correctly, (4) opencv is already available. Not worth the dependency cost. |
| Retry Logic | **Manual polling loop** with `time.sleep()` | tenacity library | tenacity is excellent for general retry patterns, but our use case is a simple create-poll-download flow with one retry scenario (HTTP errors during polling). A manual loop with `time.sleep(5)` is clearer, has zero dependencies, and matches the test script pattern exactly. |
| Retry Logic | **Manual polling loop** | backoff library | Same reasoning as tenacity. Over-engineered for a single polling loop. |
| Image Encoding | **Pillow JPEG** | turbojpeg / Pillow WebP | JPEG at quality=95 gives excellent quality with small size. WebP is slightly smaller but less universally supported by APIs. turbojpeg requires libturbojpeg system dependency. Pillow JPEG is the safe, portable choice. |
| Packaging | **requirements.txt** | pyproject.toml with `[tool.comfy]` | The `pyproject.toml` approach is for the ComfyUI Registry (a newer publishing path). For v1, a simple `requirements.txt` + GitHub URL via ComfyUI Manager is sufficient and has zero friction. Can add `pyproject.toml` later for Registry listing. |
## Installation
# Core dependencies (ComfyUI Manager runs this automatically)
# These are already installed with ComfyUI -- do NOT install separately
# torch>=2.0, numpy>=1.23
### requirements.txt
## Confidence Assessment
| Choice | Confidence | Rationale |
|--------|------------|-----------|
| Python >= 3.8 | **HIGH** | ComfyUI official docs specify minimum. Verified. |
| requests >= 2.28 | **HIGH** | Proven in existing test script. Standard in ComfyUI ecosystem. Synchronous execution is the correct model. |
| opencv-python >= 4.7 | **HIGH** | Already in project constraints. Standard for video frame extraction. Present in most ComfyUI environments. |
| Pillow >= 9.0 | **HIGH** | Standard for PIL-to-tensor conversion. Already in ComfyUI dependency tree. |
| Manual polling (no retry lib) | **HIGH** | Test script validates the pattern. ComfyUI ecosystem convention. Zero dependency overhead. |
| requirements.txt (not pyproject.toml) | **HIGH** | ComfyUI Manager convention. Reference project uses same approach. |
| No asyncio/httpx/aiohttp | **HIGH** | ComfyUI execution model is synchronous. Official docs and reference implementations confirm this. |
## Sources
- [ComfyUI Official Docs - Custom Node Walkthrough](https://docs.comfy.org/custom-nodes/walkthrough) -- HIGH confidence
- [ComfyUI Official Docs - Tensors](https://docs.comfy.org/custom-nodes/backend/tensors) -- HIGH confidence, IMAGE format [B,H,W,C] float32
- [ComfyUI Official Docs - Lifecycle](https://docs.comfy.org/custom-nodes/backend/lifecycle) -- HIGH confidence, NODE_CLASS_MAPPINGS registration
- [Reference Project: Anil-matcha/seedance2-comfyui](https://github.com/Anil-matcha/seedance2-comfyui) -- HIGH confidence, dependencies and structure
- [Existing test script seedance_video.py](file:///C:/WorkSpace/seedance_comfyui/seedance_video.py) -- HIGH confidence, validates API interaction pattern
- [AIHubMix API Documentation](https://docs.aihubmix.com/en/api/Video-Gen) -- HIGH confidence, endpoint specifications
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

# Domain Pitfalls

**Domain:** ComfyUI Custom Node Plugin for Video Generation (Seedance 2.0 via AIHubMix API)
**Researched:** 2026-04-03

## Critical Pitfalls

Mistakes that cause rewrites, security breaches, or major issues.

### Pitfall 1: Synchronous Polling Blocks ComfyUI Server Thread

**What goes wrong:** Using `time.sleep()` inside a node's `run()` method blocks ComfyUI's single-threaded aiohttp server. The UI becomes completely unresponsive -- no progress updates, no cancel button, no other interactions -- for the entire duration of the polling loop (potentially 5-15 minutes for a single video).

**Why it happens:** The test script (`seedance_video.py`) uses `time.sleep(5)` in a polling loop. This works for a CLI tool but is catastrophic inside ComfyUI's server. Developers naturally port the test script pattern into the node class without realizing ComfyUI runs on an async event loop (aiohttp).

**Consequences:** ComfyUI UI freezes entirely during generation. Users cannot cancel, queue other jobs, or interact with the interface. Multiple reports on GitHub Issue #8673 confirm this makes ComfyUI appear crashed.

**Prevention:** Despite the event loop issue, the standard practice across ComfyUI API-based nodes (Kling, Sora, reference seedance2-comfyui) is to use synchronous `requests` + `time.sleep()`. ComfyUI's execution engine is inherently synchronous per-node. The key mitigation is:
- Keep the polling interval reasonable (3-5 seconds, not longer)
- Log progress via `print()` statements so ComfyUI's console shows activity
- Accept that the UI will appear "busy" during generation (this is normal for all API-based ComfyUI nodes)
- Do NOT attempt asyncio -- ComfyUI's execution thread is synchronous, and mixing asyncio.run() with aiohttp's existing event loop causes worse problems

**Detection:** If the ComfyUI web UI shows a spinning cursor and the browser tab becomes unresponsive during video generation, this pitfall has been hit. Check the terminal -- if `print()` statements from the polling loop appear, the code is running but the UI is blocked.

**Confidence:** HIGH -- Confirmed by GitHub Issue #8673, ComfyUI architecture documentation, and the pattern used by all existing API-based custom nodes.

### Pitfall 2: API Key Hardcoded in Source Code

**What goes wrong:** API keys are committed to git, pushed to GitHub, and scraped by bots within minutes. The existing test script already has a hardcoded key on line 10 (`sk-GqYu9ThR5fLcoyzdCc834488F6574280936693D416917501`). If this file is committed as-is, the key is exposed.

**Why it happens:** During development, it is convenient to paste the API key directly into the source. The test script was written for quick validation, not for production. Developers forget to remove it before committing, or the test script gets included in the repository.

**Consequences:** Compromised API keys lead to unauthorized usage, billing charges, and potential account suspension. GitHub secret scanning bots detect keys within seconds of a push. Snyk Labs research shows thousands of ComfyUI API keys exposed on GitHub.

**Prevention:**
- The test script (`seedance_video.py`) must be listed in `.gitignore` or have its key replaced with a placeholder before any commit
- All node classes must accept `api_key` as an input parameter (STRING type), never read from a file or environment variable in v1
- Create a `.gitignore` immediately with entries for: `__pycache__/`, `*.pyc`, `.env`, `*.mp4`, `seedance_video.py` (test script with key)
- Add a pre-commit hook or GitHub Action for secret scanning if possible
- Never use `default="sk-..."` in INPUT_TYPES -- leave default empty string

**Detection:** Run `git diff --staged` before committing and search for `sk-` patterns. Check that `.gitignore` exists and covers the test script.

**Confidence:** HIGH -- The test script already contains a real key. GitHub secret scanning documentation and Snyk Labs reports confirm this is a widespread problem in ComfyUI plugins.

### Pitfall 3: Incorrect IMAGE Tensor Format (BHWC vs BCHW)

**What goes wrong:** PyTorch models typically use BCHW format (Batch, Channel, Height, Width), but ComfyUI's IMAGE type uses BHWC format (Batch, Height, Width, Channel) with float32 values in range [0.0, 1.0]. Mixing these up produces garbled images, crashes, or silent data corruption.

**Why it happens:** Developers coming from PyTorch or torchvision backgrounds instinctively use `.permute(0, 3, 1, 2)` to convert to BCHW. OpenCV also returns BGR arrays, not RGB. The conversion chain has multiple points of failure: tensor shape, channel order, value range, and dtype.

**Consequences:** Wrong shape causes `torch` dimension mismatch errors. Wrong channel order (BGR vs RGB) causes color-swapped images. Wrong value range (0-255 int instead of 0.0-1.0 float) causes pure white or pure black images. All of these are hard to debug visually.

**Prevention:** Follow the exact conversion pattern from ComfyUI official docs:
- **ComfyUI to API (IMAGE -> base64):** `[B,H,W,C] float32 [0,1]` -> select batch[0] -> `(* 255).astype(uint8)` -> `PIL.Image.fromarray()` (RGB) -> save as JPEG -> base64 encode
- **API to ComfyUI (video frames -> IMAGE):** `cv2.VideoCapture` reads BGR uint8 -> `cv2.cvtColor(BGR2RGB)` -> `astype(float32) / 255.0` -> `torch.from_numpy()` -> unsqueeze(0) for batch dimension
- Always validate: after conversion, assert tensor.shape[-1] == 3 (channels last), assert tensor.min() >= 0.0 and tensor.max() <= 1.0
- Write a unit test that does a round-trip: IMAGE -> base64 -> IMAGE and compares

**Detection:** If generated images appear with swapped colors (red becomes blue), all-white, all-black, or dimension errors appear in the console, the tensor conversion is wrong.

**Confidence:** HIGH -- Confirmed by ComfyUI official documentation (docs.comfy.org/custom-nodes/backend/datatypes) which explicitly states IMAGE is `[B,H,W,C]` float32 range `[0.0, 1.0]`.

### Pitfall 4: Loading All Video Frames Into Memory Causes OOM

**What goes wrong:** A 15-second 1080p video at 30fps is approximately 450 frames, each 1920x1080x3 bytes as uint8. That is about 2.5 GB for raw frames alone. As float32 tensors, this becomes 10 GB. Loading all frames at once crashes with Out of Memory errors, especially on systems where ComfyUI shares GPU memory with the model.

**Why it happens:** The naive approach is `cap.read()` in a loop, appending every frame to a list, then stacking. OpenCV has no built-in frame cap. Users expect to get all frames as a tensor batch.

**Consequences:** Python process crashes with MemoryError or torch OOM. On systems with 16 GB RAM, even a single 720p 10-second video can exhaust memory when other ComfyUI nodes are also loaded.

**Prevention:**
- Implement `frame_load_cap` parameter with a reasonable default (e.g., 300 frames max, which covers 10 seconds at 30fps)
- Implement `skip_first_frames` and `select_every_nth` parameters for frame sampling (follow VideoHelperSuite's pattern)
- When converting frames to tensors, process in chunks rather than loading all into a list first
- For the generation node's "first_frame" output, only extract 1 frame -- do not load the entire video
- Document memory implications in node tooltips

**Detection:** If ComfyUI crashes or becomes extremely slow after video download, memory is the issue. Monitor `torch.cuda.memory_allocated()` or system RAM during frame extraction.

**Confidence:** HIGH -- Confirmed by VideoHelperSuite GitHub Issue #163 which specifically documents OOM when loading large videos with OpenCV. The fix (frame_load_cap) is the established solution.

### Pitfall 5: Missing or Inadequate API Error Handling

**What goes wrong:** The AIHubMix API returns various HTTP status codes (401 unauthorized, 429 rate limited, 500 server error, 404 not found) and error structures (JSON with `error` as dict or string). If the node does not handle all of these, users see unhelpful Python tracebacks instead of actionable messages.

**Why it happens:** The test script uses `sys.exit()` on errors, which kills the entire Python process. This is unacceptable in ComfyUI -- the node must raise a descriptive exception, not exit the process. Additionally, the error response format varies: `data.get("error")` can be a dict with a `message` key or a plain string.

**Consequences:** Users see raw `requests.exceptions.HTTPError` or generic `KeyError` messages. No indication of whether the problem is a bad API key, rate limiting, API outage, or invalid parameters. Makes debugging extremely frustrating.

**Prevention:**
- Create a centralized `_check_response(resp)` function in `seedance_api.py` that handles all status codes:
  - 401 -> "Invalid API key. Check your AIHubMix API key in the ApiKey node."
  - 429 -> "Rate limited by AIHubMix. Wait a moment and try again."
  - 500/502/503 -> "AIHubMix server error. Try again later."
  - 404 -> "Video ID not found. The generation may have expired."
  - Other non-200 -> "Unexpected API error ({status_code}): {resp.text}"
- Handle the dual error format: `error_data.get("message") if isinstance(error_data, dict) else str(error_data)`
- Use retry with exponential backoff for transient errors (429, 500, 502, 503) -- max 3 retries
- Never use `sys.exit()` in ComfyUI node code
- Wrap the entire `run()` method in a try/except that catches `requests.exceptions.ConnectionError` and provides a clear "Cannot connect to AIHubMix API" message

**Detection:** If a failed API call produces a Python traceback referencing `requests` or `urllib3` internals instead of a human-readable message, error handling is inadequate.

**Confidence:** MEDIUM -- The error format analysis is based on the test script's existing handling (lines 143-148) and general API patterns. The AIHubMix API documentation should be consulted during implementation for the exact error response schema.

## Moderate Pitfalls

### Pitfall 6: ComfyUI Manager Incompatibility

**What goes wrong:** The plugin installs but does not appear in ComfyUI's node menu, or appears with wrong names, or fails to load silently.

**Why it happens:** Common causes:
- `__init__.py` does not export `NODE_CLASS_MAPPINGS` at module level (wrapped in a function or class)
- Import errors in node modules cause silent failure -- ComfyUI catches and logs the exception but does not surface it prominently
- Missing `requirements.txt` means dependencies are not installed
- Wrong directory structure (nested too deep, or files at wrong level)

**Prevention:**
- Follow the exact registration pattern from ARCHITECTURE.md
- `NODE_CLASS_MAPPINGS` must be a module-level dict, not inside a function
- `NODE_DISPLAY_NAME_MAPPINGS` must use the same keys as `NODE_CLASS_MAPPINGS`
- Test by cloning the repo directly into `ComfyUI/custom_nodes/seedance_comfyui/` and restarting
- Check ComfyUI's terminal output on startup for import errors related to the plugin
- Include a `requirements.txt` at the repo root with exact dependencies: `requests>=2.28`, `opencv-python>=4.7`, `Pillow>=9.0`
- Do NOT include `torch` in requirements.txt -- ComfyUI provides it

**Detection:** After restarting ComfyUI, check the terminal for lines like `[seedance_comfyui] loaded` or any import error traceback. Right-click the canvas and look for the "Seedance 2.0" category in the node menu.

**Confidence:** HIGH -- Based on ComfyUI official documentation (docs.comfy.org/custom-nodes/walkthrough), ComfyUI Manager installation docs, and the established pattern across hundreds of custom node packages.

### Pitfall 7: Cross-Platform Path Issues (Windows vs Linux)

**What goes wrong:** File paths work on the developer's machine but break for users on a different OS. Common failures: backslash vs forward slash in video URLs, `os.PathLike` TypeError when ComfyUI passes `PosixPath` or `WindowsPath` objects, and `output/seedance/` subfolder creation failing.

**Why it happens:** Windows uses backslashes, Linux/macOS uses forward slashes. `os.path.join()` handles this correctly, but hardcoded string concatenation does not. ComfyUI's `folder_paths.get_output_directory()` returns a path object that may not behave as a plain string. GitHub Issue #1834 in ComfyUI-Manager documents `os.PathLike` TypeError issues on Windows.

**Prevention:**
- Always use `os.path.join()` or `pathlib.Path` for path construction -- never string concatenation with `/` or `\`
- When creating output subdirectories, use `os.makedirs(path, exist_ok=True)`
- Convert `PosixPath`/`WindowsPath` to string explicitly: `str(folder_paths.get_output_directory())`
- Test on both Windows and Linux if possible, or at minimum use `pathlib.Path` which is OS-agnostic
- For the video download path, construct as: `Path(folder_paths.get_output_directory()) / "seedance" / filename`

**Detection:** If users report `TypeError: expected str, bytes or os.PathLike object, not PosixPath` or file-not-found errors on a different OS, path handling is the issue.

**Confidence:** MEDIUM -- Based on ComfyUI-Manager Issue #1834 (Windows PathLike TypeError) and general cross-platform Python knowledge. Not verified on actual Windows ComfyUI installation during this research.

### Pitfall 8: Missing or Conflicting Dependencies

**What goes wrong:** The plugin fails to import because `requests`, `cv2`, or `PIL` are not installed, or conflicts arise with versions already in the ComfyUI environment.

**Why it happens:** ComfyUI does not isolate custom node dependencies. All custom nodes share the same Python environment. If the plugin requires `opencv-python>=4.7` but another node installed `opencv-python-headless==4.5`, pip may produce a broken installation.

**Prevention:**
- Pin minimum versions in `requirements.txt`, not exact versions: `requests>=2.28`, not `requests==2.28.0`
- Do NOT include `torch`, `numpy`, or `Pillow` in requirements.txt -- ComfyUI already provides these. Adding them can cause version conflicts. ComfyUI's blog on dependency resolution explicitly warns about this.
- Use `opencv-python` (not `opencv-python-headless`) since ComfyUI desktop bundles the full version
- Consider using an `install.py` script for complex dependency checks (optional for v1)
- Document prerequisites clearly in README

**Detection:** Import errors on first use: `ModuleNotFoundError: No module named 'requests'` or `ImportError: cannot import name 'x' from 'cv2'`.

**Confidence:** HIGH -- Based on ComfyUI blog post on dependency resolution and the established practice across the custom node ecosystem.

### Pitfall 9: Polling Timeout Without User Feedback

**What goes wrong:** Video generation can take 5-15 minutes. If the polling loop has no progress indication, users assume the node is frozen and kill the ComfyUI process, potentially corrupting workflows.

**Why it happens:** The AIHubMix API provides a `progress` field (0-100 percentage) during `in_progress` status, but developers may not surface this to the user. ComfyUI nodes do not have a built-in progress bar API for the web UI.

**Prevention:**
- Use `print()` statements in the polling loop to log progress to the ComfyUI terminal (this is the standard pattern -- all API-based nodes do this)
- Include the video ID and progress percentage in each log line
- Implement a `max_wait` timeout (default 900 seconds / 15 minutes) with a clear error message: `RuntimeError("Video generation timed out after 15 minutes. The video may still be processing on AIHubMix. Video ID: {id}")`
- Make `max_wait` configurable as an advanced parameter on the node
- Consider logging the AIHubMix progress percentage: `print(f"[Seedance] Video {video_id}: {status} ({progress}%)")`

**Detection:** If users report "node stuck" without any console output from the plugin, progress logging is missing or the polling interval is too long.

**Confidence:** HIGH -- The test script already implements progress display (lines 134-137). GitHub Issues #8673 and #9007 confirm the importance of user feedback during long-running operations.

## Minor Pitfalls

### Pitfall 10: Video Download URL Expiration

**What goes wrong:** The AIHubMix video download URL (`/v1/videos/{id}/content`) may expire after a certain time. If a user saves a workflow with a `video_url` output and tries to use it later, the download fails.

**Why it happens:** Cloud API providers typically use signed URLs that expire. The exact TTL for AIHubMix is not documented in the research sources.

**Prevention:**
- Document that `video_url` outputs are ephemeral and should be saved immediately
- The Video Saver node should be used right after generation, not hours later
- Consider adding a warning if the download fails with 403/404

**Detection:** If download works immediately after generation but fails hours later, URL expiration is the cause.

**Confidence:** LOW -- Based on general API behavior patterns. The exact AIHubMix URL expiration policy was not found in the documentation.

### Pitfall 11: Data URI Size Limits for Image Input

**What goes wrong:** Converting a high-resolution image (4K+) to base64 produces a very large data URI (potentially 10+ MB). This may exceed API request body limits or cause slow uploads.

**Why it happens:** No size validation is performed on input images before base64 encoding. Users may feed 8K images from ComfyUI's image loading pipeline.

**Prevention:**
- Resize images larger than a threshold (e.g., 2048px on the longest side) before encoding
- Use JPEG compression (quality=95) rather than PNG for base64 encoding to reduce size
- The ARCHITECTURE.md pattern already specifies JPEG encoding, which is correct

**Detection:** If the API returns 413 (Payload Too Large) on I2V requests with high-resolution images.

**Confidence:** LOW -- Based on general API size limit knowledge. AIHubMix's specific limits are not documented in the available sources.

### Pitfall 12: Silent Node Failure on Import Errors

**What goes wrong:** If `import cv2` fails because opencv-python is not installed, ComfyUI silently skips the entire plugin. All nodes disappear from the menu with only a small error in the terminal.

**Why it happens:** ComfyUI's custom node loader wraps each plugin's `__init__.py` import in a try/except. Import failures are logged but do not prevent ComfyUI from starting.

**Prevention:**
- Use lazy imports: only `import cv2` inside the methods that need it, not at module top level
- Provide a fallback error message: if cv2 is not available, the Video Saver node's `run()` method should raise `ImportError("opencv-python is required for video frame extraction. Install via: pip install opencv-python")`
- This way, generation nodes (which do not need cv2) still work even if opencv is missing

**Detection:** If nodes disappear from the ComfyUI menu after adding new imports, check the terminal for import error tracebacks.

**Confidence:** HIGH -- This is a well-known ComfyUI behavior documented in community forums and the official custom node walkthrough.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Project setup / .gitignore | Hardcoded API key in test script (Pitfall 2) | Create `.gitignore` before first commit, exclude `seedance_video.py` or replace key with placeholder |
| API client implementation | Inadequate error handling (Pitfall 5) | Build `_check_response()` function first, before any node classes |
| API client implementation | Polling blocks server thread (Pitfall 1) | Accept synchronous pattern as standard; add progress logging |
| Node class implementation | Incorrect tensor format (Pitfall 3) | Write round-trip test: IMAGE -> base64 -> IMAGE before building nodes |
| Video saver implementation | OOM from loading all frames (Pitfall 4) | Implement `frame_load_cap` from the start, do not add it later |
| Video saver implementation | Cross-platform path issues (Pitfall 7) | Use `pathlib.Path` throughout, test on Windows |
| Package / publish | ComfyUI Manager incompatibility (Pitfall 6) | Test clone into `custom_nodes/` before publishing |
| Package / publish | Missing/conflicting deps (Pitfall 8) | Do not include `torch`/`numpy` in requirements.txt |
| All phases | Silent import failures (Pitfall 12) | Use lazy imports for heavy dependencies like cv2 |

## Top 3 Risks by Severity

1. **API Key Exposure (Pitfall 2)** -- IMMEDIATE action required. The test script has a real key. Create `.gitignore` before ANY git operation.
2. **Tensor Format Mismatch (Pitfall 3)** -- Will cause incorrect output for every user. Validate conversion with a test before building any node.
3. **OOM on Large Videos (Pitfall 4)** -- Will crash ComfyUI for users generating 1080p 15-second videos. Implement frame cap from day one.

## Sources

- [ComfyUI GitHub Issue #8673](https://github.com/comfyanonymous/ComfyUI/issues/8673) -- `time.sleep()` blocking the server event loop (HIGH confidence)
- [ComfyUI Official Docs - Datatypes](https://docs.comfy.org/custom-nodes/backend/datatypes) -- IMAGE tensor format BHWC float32 [0.0, 1.0] (HIGH confidence)
- [VideoHelperSuite GitHub Issue #163](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite/issues/163) -- OOM when loading large videos with OpenCV (HIGH confidence)
- [ComfyUI-Manager GitHub Issue #1834](https://github.com/ltdrdata/ComfyUI-Manager/issues/1834) -- `os.PathLike` TypeError on Windows (MEDIUM confidence)
- [ComfyUI Blog - Dependency Resolution](https://blog.comfy.org/p/dependency-resolution-and-custom) -- Best practices for dependency management (MEDIUM confidence)
- [ComfyUI Official Docs - Custom Node Walkthrough](https://docs.comfy.org/custom-nodes/walkthrough) -- Registration pattern, import behavior (HIGH confidence)
- [Snyk Labs - ComfyUI Security](https://snyk.io/blog/comfyui-security) -- API key exposure on GitHub (MEDIUM confidence)
- [Test script seedance_video.py](file:///C:/WorkSpace/seedance_comfyui/seedance_video.py) -- Contains hardcoded API key on line 10, error handling pattern, progress display (HIGH confidence -- directly observed)
- [AIHubMix Video Generation API](https://docs.aihubmix.com/en/api/Video-Gen) -- API error response format (MEDIUM confidence -- not fully verified)

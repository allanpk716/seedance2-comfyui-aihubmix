# Phase 4: Publish - Research

**Researched:** 2026-04-03
**Domain:** GitHub repository setup, README documentation, ComfyUI Manager compatibility
**Confidence:** HIGH

## Summary

Phase 4 is a documentation-and-publishing phase with no new code development. The project code is complete (6 nodes, API client, 115 passing tests). This phase focuses on three deliverables: (1) a clean, publicly accessible GitHub repository compatible with ComfyUI Manager's "Install via Git URL" feature, (2) bilingual README documentation with installation instructions and node reference, and (3) an MIT LICENSE file.

The existing repository structure already satisfies ComfyUI Manager's structural requirements (`__init__.py` with `NODE_CLASS_MAPPINGS` + `requirements.txt` at repo root). The `.gitignore` needs cleanup (removing artifact files `=4.7` and `.no-windows` that are currently tracked, adding standard Python patterns). Several dev-only files (`.planning/`, `.omc/`, `.claude/`, `CLAUDE.md`, `seedance_video.py`) must be added to `.gitignore` before the initial public push.

No remote repository exists yet (`git remote -v` shows nothing). The `gh` CLI (v2.83.2) is available for creating the GitHub repo programmatically. Git (v2.45.1) is installed. The project uses relative imports (`from .nodes import ...`, `from .api_client import ...`) which is correct for ComfyUI's module loading.

**Primary recommendation:** Clean up `.gitignore`, remove tracked artifacts, write README.md + README_CN.md + LICENSE, create the GitHub repo via `gh repo create`, and push. Verify ComfyUI Manager compatibility by confirming the repo root structure.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-18:** Bilingual README -- separate files: `README.md` (English) + `README_CN.md` (Chinese). Language switcher link at top of each file.
- **D-19:** Example workflows use text description format (not JSON export). Cover T2V and I2V workflows only, matching ROADMAP success criteria #3.
- **D-20:** README sections: Installation guide, Node reference (all 6 nodes with input/output summary), Example workflows (T2V + I2V), FAQ/troubleshooting (API key setup, resolutions, duration, common errors).
- **D-20a:** Installation guide covers both ComfyUI Manager "Install via Git URL" and manual `git clone` into `custom_nodes/`.
- **D-21:** MIT License.
- **D-22:** Repository name: `seedance2-comfyui-aihubmix`. Public visibility.
- **D-23:** Minimal files only -- no issue templates, no screenshots, no extra files. README, LICENSE, requirements.txt, .gitignore, source code, and tests.
- **D-23a:** Include `tests/` directory in the published repo (good practice, users can run tests).
- **D-24:** Clean up `.gitignore` -- remove artifacts (`=4.7`, `.no-windows`), add standard Python gitignore patterns (build/, dist/, *.egg-info, .env, __pycache__/, etc.).
- **D-25:** Audit for dev-only files that shouldn't be published. Ensure `seedance_video.py` (test script), `.env`, `.planning/`, `.omc/`, `.claude/`, `CLAUDE.md` are all gitignored.
- **D-26:** Verify ComfyUI Manager "Install via Git URL" compatibility -- repo structure must match what ComfyUI Manager expects (repo root contains `__init__.py` with `NODE_CLASS_MAPPINGS` + `requirements.txt`).

### Claude's Discretion
- README formatting and section ordering
- Node reference table layout
- Example workflow text description phrasing
- FAQ question selection
- .gitignore specific patterns
- ComfyUI Manager verification steps
- Git commit message format

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PFND-04 | Plugin is installable via ComfyUI Manager "Install via Git URL" | ComfyUI Manager requires: (1) git repo, (2) `__init__.py` with `NODE_CLASS_MAPPINGS` at repo root, (3) `requirements.txt` for auto pip install. Current repo structure satisfies all three. |
</phase_requirements>

## Standard Stack

This is a documentation/publishing phase. No new libraries or frameworks are needed. The existing stack is already complete.

### Tools Required

| Tool | Version | Purpose | Status |
|------|---------|---------|--------|
| git | 2.45.1 | Version control, repo init, remote setup | Available |
| gh CLI | 2.83.2 | Create GitHub repo, push code | Available |
| Python | 3.11.9 | Run existing test suite for verification | Available |
| pytest | 9.0.2 | Run 115 existing tests to verify nothing broken | Available |

## Architecture Patterns

### ComfyUI Manager Installation Flow

When a user clicks "Install via Git URL" in ComfyUI Manager:

```
1. ComfyUI Manager calls: git clone <URL> into ComfyUI/custom_nodes/<repo-name>/
2. If requirements.txt exists at repo root: pip install -r requirements.txt
3. If install.py exists at repo root: python install.py  (we do NOT need this)
4. User restarts ComfyUI
5. ComfyUI discovers __init__.py and loads NODE_CLASS_MAPPINGS
```

**Source:** [ComfyUI Official Docs - Publishing to the Manager](https://docs.comfy.org/custom-nodes/backend/manager)

### Required Repo Structure (Verified Against Current Code)

```
seedance2-comfyui-aihubmix/       # Repo root = directory name from clone
  __init__.py                      # NODE_CLASS_MAPPINGS + NODE_DISPLAY_NAME_MAPPINGS
  nodes.py                         # 6 node classes
  api_client.py                    # API communication module
  requirements.txt                 # requests, Pillow, numpy, opencv-python
  .gitignore                       # Standard Python patterns
  README.md                        # English documentation
  README_CN.md                     # Chinese documentation
  LICENSE                          # MIT license
  tests/                           # Test suite (per D-23a)
    __init__.py
    conftest.py
    test_api_client.py
    test_nodes.py
    test_registration.py
```

### Current Repo State (Issues to Fix)

| Issue | File | Action Required |
|-------|------|-----------------|
| Tracked artifact file | `=4.7` (empty file from pip typo) | Remove from git tracking, add to .gitignore |
| Tracked empty marker | `.no-windows` | Remove from git tracking, add to .gitignore |
| Dev-only files tracked | `.planning/`, `CLAUDE.md` | Add to .gitignore, remove from tracking |
| Dev test script tracked | `seedance_video.py` | Already in .gitignore, but verify not tracked |
| Missing standard patterns | `.gitignore` | Add `__pycache__/`, `*.egg-info/`, `.env`, `.omc/`, `.claude/`, etc. |
| Missing files | `README.md`, `README_CN.md`, `LICENSE` | Create new files |

### .gitignore Recommended Content

```gitignore
# Dev test script
seedance_video.py

# Environment and secrets
.env
.env.*

# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
*.egg
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Artifact files from pip typos
=*

# Dev/planning (not for published repo)
.planning/
.omc/
.claude/
CLAUDE.md
.no-windows
.pytest_cache/

# pytest
.pytest_cache/
```

### ComfyUI Manager Compatibility Checklist

These must be TRUE for "Install via Git URL" to work:

1. **Public GitHub repo** -- `gh repo create` with `--public` flag
2. **`__init__.py` at repo root** with `NODE_CLASS_MAPPINGS` dict -- VERIFIED: exists and correct
3. **`requirements.txt` at repo root** -- VERIFIED: exists with 4 dependencies
4. **Relative imports work** when loaded as package -- VERIFIED: `from .nodes import ...` and `from .api_client import ...`
5. **No hardcoded paths** that break outside dev environment -- VERIFIED: only `folder_paths` (ComfyUI built-in) used dynamically

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GitHub repo creation | Manual web UI steps | `gh repo create` CLI | Faster, scriptable, consistent. `gh` v2.83.2 is already installed. |
| .gitignore patterns | Custom ad-hoc patterns | GitHub Python .gitignore template | Covers edge cases (`.egg-info`, `__pycache__`, `.pytest_cache`) that are easy to miss. |
| License text | Custom license file | MIT License standard text from choosealicense.com or `gh` | Standard text avoids legal ambiguity. |

## Common Pitfalls

### Pitfall 1: Tracked Dev Files Leaked to Public Repo
**What goes wrong:** `.planning/`, `CLAUDE.md`, `seedance_video.py` pushed to public GitHub, exposing internal planning artifacts and confusing users.
**Why it happens:** `.gitignore` only prevents future additions; files already tracked by git are NOT affected by adding them to `.gitignore`.
**How to avoid:** Run `git rm --cached` for each dev file BEFORE the initial push. Then add to `.gitignore`. Verify with `git status`.
**Warning signs:** `git ls-files | grep -E '^\.(planning|omc|claude)|CLAUDE\.md|seedance_video'` returns results.

### Pitfall 2: Artifact Files (`=4.7`, `.no-windows`) Published
**What goes wrong:** Empty files from pip typos or dev markers appear in the repo root, making it look unprofessional.
**Why it happens:** These files were created during development and `git add` tracked them before `.gitignore` was comprehensive.
**How to avoid:** `git rm --cached =4.7 .no-windows` then add `=*` and `.no-windows` to `.gitignore`.

### Pitfall 3: README References muapi.ai Instead of AIHubMix
**What goes wrong:** README content copied from the reference project still mentions muapi.ai, confusing users about which API service to use.
**Why it happens:** The reference project (Anil-matcha/seedance2-comfyui) uses muapi.ai. Copy-pasting its README structure without updating all references.
**How to avoid:** Search README for "muapi" and "muapi.ai" before committing. All references should point to AIHubMix (aihubmix.com) and its API docs.

### Pitfall 4: Bilingual Files Not Cross-Linked
**What goes wrong:** Users land on one language version and can't find the other.
**Why it happens:** Forgot to add language switcher links per D-18.
**How to avoid:** First line of each README: `[English](./README.md) | [中文](./README_CN.md)` (or vice versa).

### Pitfall 5: ComfyUI Manager Can't Find Nodes After Install
**What goes wrong:** User installs via "Install via Git URL", restarts ComfyUI, but nodes don't appear in the menu.
**Why it happens:** Usually caused by: (a) `__init__.py` not at repo root, (b) `NODE_CLASS_MAPPINGS` not exported, (c) import errors in node classes, (d) directory name conflicts.
**How to avoid:** Verify the repo structure. The repo name `seedance2-comfyui-aihubmix` will be the directory name in `custom_nodes/`. ComfyUI scans all subdirectories of `custom_nodes/` and imports `__init__.py` from each. Our relative imports (`from .nodes import ...`) work correctly because ComfyUI treats each subdirectory as a Python package.
**Warning signs:** Check ComfyUI console output for import errors after restart.

### Pitfall 6: Forgetting to Remove `.gitignore` Entry for `=4.7`
**What goes wrong:** The `.gitignore` currently lists `=4.7` as a specific filename entry. While this works, `=*` is a more robust pattern that catches any similar pip typo artifacts.
**Why it happens:** The current `.gitignore` was written incrementally during development.
**How to avoid:** Replace the specific `=4.7` entry with `=*` pattern in the new comprehensive `.gitignore`.

## Code Examples

### GitHub Repo Creation via gh CLI

```bash
# Create public repo on GitHub (no local git init needed -- already done)
gh repo create seedance2-comfyui-aihubmix --public --description "ComfyUI custom nodes for Seedance 2.0 video generation via AIHubMix API" --source=. --push=false

# Add remote to existing local repo
git remote add origin https://github.com/<username>/seedance2-comfyui-aihubmix.git
```

### Removing Tracked Dev Files

```bash
# Remove files from git tracking (keeps on disk)
git rm --cached .planning/ -r
git rm --cached CLAUDE.md
git rm --cached "=4.7"
git rm --cached .no-windows
git rm --cached .pytest_cache/ -r 2>/dev/null
```

### MIT License Template

```
MIT License

Copyright (c) 2026 AIHubMix

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### README Structure (Per D-18, D-19, D-20)

```
README.md (English):
  - Language switcher: [English] | [中文](./README_CN.md)
  - Badges (optional): MIT License, ComfyUI Custom Node
  - What is Seedance 2.0? (brief description)
  - Features (T2V, I2V, Extend, Omni Reference, Save Video)
  - Installation (Manager + Manual, per D-20a)
  - Quick Start (4 steps: get API key, install, add node, generate)
  - Node Reference (table of all 6 nodes with inputs/outputs)
  - Example Workflows (T2V + I2V text descriptions per D-19)
  - FAQ/Troubleshooting (per D-20)
  - Requirements
  - License

README_CN.md (Chinese):
  - Same structure, translated to Chinese
  - Language switcher: [English](./README.md) | [中文]
```

### Node Reference Data (from nodes.py)

6 registered nodes for documentation:

| Node Class | Display Name | Inputs | Outputs |
|------------|-------------|--------|---------|
| SeedanceApiKey | Seedance 2.0 API Key | api_key (STRING) | api_key (STRING) |
| SeedanceTextToVideo | Seedance 2.0 Text to Video | prompt (STRING, required); api_key, duration (4-15), resolution (480p/720p/1080p), ratio (6 options) | video_url (STRING), video_id (STRING) |
| SeedanceImageToVideo | Seedance 2.0 Image to Video | image (IMAGE, required), prompt (STRING, required); api_key, duration, resolution, ratio | video_url (STRING), video_id (STRING) |
| SeedanceSaveVideo | Seedance 2.0 Save Video | video_url (STRING, required); filename_prefix, subfolder, frame_load_cap (1-1000, default 16) | frames (IMAGE), first_frame_path (STRING), video_path (STRING) |
| SeedanceExtendVideo | Seedance 2.0 Video Extend | video_id (STRING, required), prompt (STRING, required); api_key, duration, resolution, ratio | video_url (STRING), video_id (STRING) |
| SeedanceOmniReference | Seedance 2.0 Omni Reference | prompt (STRING, required); api_key, duration, resolution, ratio, image_1..image_9 (IMAGE), video_url_1..video_url_3 (STRING) | video_url (STRING), video_id (STRING) |

### Example Workflow Text Descriptions (Per D-19)

**T2V Workflow:**
```
1. Add "Seedance 2.0 API Key" node -- paste your AIHubMix API key
2. Add "Seedance 2.0 Text to Video" node -- enter prompt, set resolution/duration
3. Connect API Key node output -> T2V node api_key input
4. Add "Seedance 2.0 Save Video" node
5. Connect T2V video_url output -> Save Video node video_url input
6. Click "Queue Prompt" to generate
```

**I2V Workflow:**
```
1. Add "Seedance 2.0 API Key" node -- paste your AIHubMix API key
2. Add a "Load Image" node (built-in ComfyUI) -- select your reference image
3. Add "Seedance 2.0 Image to Video" node -- enter prompt, set resolution/duration
4. Connect API Key -> I2V api_key input
5. Connect Load Image IMAGE output -> I2V image input
6. Add "Seedance 2.0 Save Video" node
7. Connect I2V video_url output -> Save Video node video_url input
8. Click "Queue Prompt" to generate
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual `custom-node-list.json` PR | "Install via Git URL" works without registry PR | ComfyUI Manager v2+ | No need to submit PR to ComfyUI-Manager for "Install via Git URL" to work. Registry listing is optional for discoverability. |
| pyproject.toml + ComfyUI Registry | requirements.txt + GitHub URL | 2024-2025 | v1 uses requirements.txt (simpler). Registry listing can be added later. |

**Note on ComfyUI Registry:** The ComfyUI Registry (via `pyproject.toml`) is a newer publishing path that makes nodes searchable in ComfyUI Manager without knowing the URL. For v1, the "Install via Git URL" path is sufficient per project decisions. Registry listing can be added as a future enhancement.

## Open Questions

1. **GitHub username/organization for repo creation**
   - What we know: Repo name is `seedance2-comfyui-aihubmix` (D-22), but the GitHub owner (user or org) is not specified.
   - What's unclear: Whether to create under the user's personal account or an organization.
   - Recommendation: Planner should include a task step to determine the GitHub owner. The `gh repo create` command will default to the authenticated user's account.

2. **Copyright holder for MIT License**
   - What we know: D-21 specifies MIT License.
   - What's unclear: Whether the copyright holder should be "AIHubMix", the developer's name, or something else.
   - Recommendation: Use "AIHubMix" as the copyright holder since this is a plugin for their API service. Planner should confirm with user if unclear.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| git | Repo management, push to GitHub | Yes | 2.45.1 | -- |
| gh CLI | Create GitHub repo | Yes | 2.83.2 | Manual GitHub web UI |
| Python | Run tests for verification | Yes | 3.11.9 | -- |
| pytest | Verify 115 existing tests pass | Yes | 9.0.2 | -- |
| Internet access | Push to GitHub, verify ComfyUI Manager docs | Yes | -- | -- |

**Missing dependencies with no fallback:**
- None -- all required tools are available.

**Missing dependencies with fallback:**
- None.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | None (defaults) |
| Quick run command | `python -m pytest tests/ -x -q` |
| Full suite command | `python -m pytest tests/ -v` |

### Phase Requirements -- Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PFND-04 | Plugin installable via ComfyUI Manager | Manual verification (no automated test for Manager integration) | N/A | N/A |
| -- | Node registration correct | Unit | `python -m pytest tests/test_registration.py -x` | Yes |
| -- | All node classes functional | Unit | `python -m pytest tests/test_nodes.py -x` | Yes |
| -- | API client functional | Unit | `python -m pytest tests/test_api_client.py -x` | Yes |

**Note:** PFND-04 (ComfyUI Manager installability) is verified by structural correctness (`__init__.py` with `NODE_CLASS_MAPPINGS` at repo root + `requirements.txt`), not by an automated test. The existing 115 tests verify code correctness; the publish phase verifies structural correctness through repo structure audit.

### Sampling Rate
- **Per task commit:** `python -m pytest tests/ -x -q` (30 seconds)
- **Per wave merge:** `python -m pytest tests/ -v` (60 seconds)
- **Phase gate:** Full suite green + manual verification of "Install via Git URL" instructions

### Wave 0 Gaps
None -- existing test infrastructure covers all code-level requirements. PFND-04 is a structural/publishing requirement verified by inspection.

## Sources

### Primary (HIGH confidence)
- [ComfyUI Official Docs - Publishing to the Manager](https://docs.comfy.org/custom-nodes/backend/manager) -- ComfyUI Manager installation flow, requirements.txt handling, optional install.py
- [ComfyUI Official Docs - Install Custom Nodes](https://docs.comfy.org/installation/install_custom_node) -- Three installation methods (Manager, Git, ZIP)
- [Reference Project: Anil-matcha/seedance2-comfyui](https://github.com/Anil-matcha/seedance2-comfyui) -- README structure reference, MIT License example

### Secondary (MEDIUM confidence)
- [ComfyUI-Manager GitHub](https://github.com/Comfy-Org/ComfyUI-Manager) -- Manager source code and custom-node-list.json schema
- Existing codebase files (`__init__.py`, `nodes.py`, `api_client.py`, `requirements.txt`, `.gitignore`) -- Verified repo structure, node definitions, imports

## Metadata

**Confidence breakdown:**
- Standard stack (tools): HIGH -- all tools verified present on the machine
- Architecture (ComfyUI Manager compatibility): HIGH -- verified against official docs and current repo structure
- Pitfalls: HIGH -- common publishing issues well-documented, specific artifact files identified in git tracking
- README content: HIGH -- node data extracted from actual source code, not guessed

**Research date:** 2026-04-03
**Valid until:** 2026-05-03 (stable -- documentation patterns don't change rapidly)

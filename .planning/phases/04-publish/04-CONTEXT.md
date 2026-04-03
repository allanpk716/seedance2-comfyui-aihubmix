# Phase 4: Publish - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

GitHub repository setup, README documentation, license, and ComfyUI Manager installation compatibility. Users can install the plugin via ComfyUI Manager "Install via Git URL" and get started from a README.

This phase does NOT include: new node development, API changes, or feature additions.

</domain>

<decisions>
## Implementation Decisions

### README & Documentation
- **D-18:** Bilingual README — separate files: `README.md` (English) + `README_CN.md` (Chinese). Language switcher link at top of each file.
- **D-19:** Example workflows use text description format (not JSON export). Cover T2V and I2V workflows only, matching ROADMAP success criteria #3.
- **D-20:** README sections: Installation guide, Node reference (all 6 nodes with input/output summary), Example workflows (T2V + I2V), FAQ/troubleshooting (API key setup, resolutions, duration, common errors).
- **D-20a:** Installation guide covers both ComfyUI Manager "Install via Git URL" and manual `git clone` into `custom_nodes/`.

### Repo Setup & License
- **D-21:** MIT License.
- **D-22:** Repository name: `seedance2-comfyui-aihubmix`. Public visibility.
- **D-23:** Minimal files only — no issue templates, no screenshots, no extra files. README, LICENSE, requirements.txt, .gitignore, source code, and tests.
- **D-23a:** Include `tests/` directory in the published repo (good practice, users can run tests).

### Repo Cleanup & Verification
- **D-24:** Clean up `.gitignore` — remove artifacts (`=4.7`, `.no-windows`), add standard Python gitignore patterns (build/, dist/, *.egg-info, .env, __pycache__/, etc.).
- **D-25:** Audit for dev-only files that shouldn't be published. Ensure `seedance_video.py` (test script), `.env`, `.planning/`, `.omc/`, `.claude/`, `CLAUDE.md` are all gitignored.
- **D-26:** Verify ComfyUI Manager "Install via Git URL" compatibility — repo structure must match what ComfyUI Manager expects (repo root contains `__init__.py` with `NODE_CLASS_MAPPINGS` + `requirements.txt`).

### Claude's Discretion
- README formatting and section ordering
- Node reference table layout
- Example workflow text description phrasing
- FAQ question selection
- .gitignore specific patterns
- ComfyUI Manager verification steps
- Git commit message format

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Implementation
- `__init__.py` — Node registration (NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS). Must be verified as ComfyUI Manager compatible.
- `nodes.py` — All 6 node classes. Reference for node descriptions in README.
- `api_client.py` — API client module. Reference for error messages in FAQ.
- `requirements.txt` — Dependencies that ComfyUI Manager auto-installs.

### ComfyUI Manager Reference
- ComfyUI Manager "Install via Git URL": clones the repo into `ComfyUI/custom_nodes/{repo-name}/`, then runs `pip install -r requirements.txt` if present. The repo root must have `__init__.py` with `NODE_CLASS_MAPPINGS`.

### External Docs
- AIHubMix API docs: https://docs.aihubmix.com/en/api/Video-Gen — for README links and parameter documentation
- AIHubMix signup: https://aihubmix.com — for README installation guide

### Reference Project
- https://github.com/Anil-matcha/seedance2-comfyui — Original project (may no longer be accessible). README structure reference.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `__init__.py`: 6 nodes registered — SeedanceApiKey, SeedanceTextToVideo, SeedanceImageToVideo, SeedanceSaveVideo, SeedanceExtendVideo, SeedanceOmniReference. Category: "Seedance 2.0".
- `requirements.txt`: 4 dependencies (requests, Pillow, numpy, opencv-python). Already correct.
- `.gitignore`: Exists but needs cleanup.

### Established Patterns
- Error messages in Chinese per D-08 — FAQ should reflect these messages.
- SIZE_MAP: 480p/720p/1080p with 6 aspect ratios — document in README node reference.
- Model ID: `doubao-seedance-2-0-260128` — should appear in README.

### Integration Points
- ComfyUI Manager: expects `__init__.py` at repo root with `NODE_CLASS_MAPPINGS` export. Current structure matches.
- GitHub: needs `git init`, remote setup, and initial push.

</code_context>

<specifics>
## Specific Ideas

- Node display names in ComfyUI: "Seedance 2.0 API Key", "Seedance 2.0 Text to Video", etc. — use these in README.
- T2V example: API Key node → T2V node → prompt + resolution → Save Video node
- I2V example: Load Image → I2V node → prompt + image → Save Video node
- FAQ should mention: video duration 4-15s, supported resolutions, where to get AIHubMix API key
- Link to AIHubMix in README for users who don't have an account yet

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-publish*
*Context gathered: 2026-04-03*

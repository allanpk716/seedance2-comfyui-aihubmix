# Phase 4: Publish - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 04-publish
**Areas discussed:** README & Documentation, Repo Setup & License, Repo Cleanup & Verification

---

## README & Documentation

### README Language

| Option | Description | Selected |
|--------|-------------|----------|
| English only | Single language, broader reach | |
| Chinese only | Matches error messages | |
| Bilingual (EN + CN) | Separate files, broader reach + Chinese users | ✓ |

**User's choice:** Bilingual (EN + CN) — separate files
**Notes:** README.md (English) + README_CN.md (Chinese) with language switcher links

### Bilingual Format

| Option | Description | Selected |
|--------|-------------|----------|
| Separate files | README.md + README_CN.md, clean separation | ✓ |
| Combined in one file | All in README.md, gets long | |

**User's choice:** Separate files

### Example Workflow Format

| Option | Description | Selected |
|--------|-------------|----------|
| Text description | Step-by-step text, always renders | ✓ |
| Workflow JSON file | Downloadable JSON, drag-drop into ComfyUI | |
| Both text + JSON | Best UX but more maintenance | |

**User's choice:** Text description

### README Sections

| Option | Selected |
|--------|----------|
| Installation guide | ✓ |
| Node reference | ✓ |
| Example workflows | ✓ |
| FAQ / troubleshooting | ✓ |

**User's choice:** All four sections included

### Example Workflow Coverage

| Option | Description | Selected |
|--------|-------------|----------|
| T2V + I2V only | Most common use cases | ✓ |
| All generation nodes | T2V, I2V, Extend, Omni | |
| T2V + I2V + Save Video | Practical flow | |

**User's choice:** T2V + I2V only (matches ROADMAP success criteria #3)

---

## Repo Setup & License

### License

| Option | Description | Selected |
|--------|-------------|----------|
| MIT License | Permissive, widely used | ✓ |
| GPL-3.0 | Strong copyleft | |
| Apache-2.0 | Permissive with patent grant | |

**User's choice:** MIT License

### Repository Name

| Option | Selected |
|--------|----------|
| seedance-comfyui | |
| seedance-aihubmix-comfyui | |
| seedance2-comfyui-aihubmix | ✓ |

**User's choice:** seedance2-comfyui-aihubmix

### Visibility

| Option | Selected |
|--------|----------|
| Public | ✓ |
| Private | |

**User's choice:** Public (required for ComfyUI Manager "Install via Git URL")

### Extra Files

| Option | Selected |
|--------|----------|
| Issue templates | |
| Node screenshots | |
| Keep it minimal | ✓ |

**User's choice:** Minimal — README, LICENSE, requirements.txt, .gitignore, source, tests only

### Tests in Published Repo

| Option | Selected |
|--------|----------|
| Include tests | ✓ |
| Exclude tests | |

**User's choice:** Include tests/ directory

---

## Repo Cleanup & Verification

### .gitignore Cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Clean up + expand | Remove artifacts, add standard Python patterns | ✓ |
| Remove artifacts only | Minimal changes | |

**User's choice:** Clean up + expand with standard Python gitignore patterns

### ComfyUI Manager Verification

| Option | Selected |
|--------|----------|
| Claude verifies compatibility | ✓ |
| Skip verification | |

**User's choice:** Claude verifies ComfyUI Manager "Install via Git URL" compatibility

### Dev File Audit

| Option | Selected |
|--------|----------|
| Audit and gitignore | ✓ |
| Already handled | |

**User's choice:** Audit for dev-only files (seedance_video.py, .env, .planning/, .omc/, .claude/, CLAUDE.md) and gitignore

---

## Claude's Discretion

- README formatting, section ordering, phrasing
- Node reference table layout
- FAQ question selection
- .gitignore specific patterns
- ComfyUI Manager verification steps
- Git commit message format

## Deferred Ideas

None — discussion stayed within phase scope.

# Phase 2: Image-to-Video + Video Saver - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 02-image-to-video-video-saver
**Areas discussed:** I2V 输出策略, Save Video 节点设计, 图片转换细节

---

## I2V 输出策略

| Option | Description | Selected |
|--------|-------------|----------|
| 跟 T2V 一致 | 输出 (video_url, video_id) — 简单统一，Save Video 负责帧提取 | ✓ |
| 加上 first_frame | 输出 (video_url, first_frame, video_id) — 用户可直接预览但增加复杂度 | |
| Claude 你决定 | Claude 自行决定 | |

**User's choice:** 跟 T2V 一致（推荐）
**Notes:** Phase 3 要求所有生成节点输出 first_frame，但可以在 Phase 3 统一修改 T2V/I2V/Extend/Omni 的输出格式。Phase 2 保持简单。

---

## Save Video 节点设计

| Option | Description | Selected |
|--------|-------------|----------|
| 全面输出（推荐） | 输出 (IMAGE, STRING, STRING) = (frames, first_frame_path, video_path) | ✓ |
| 精简输出 | 输出 (IMAGE, STRING) = (frames, video_path) | |
| Claude 你决定 | Claude 自行决定 | |

**User's choice:** 全面输出（推荐）
**Notes:** frames 用于下游节点处理，first_frame_path 用于首帧预览，video_path 用于视频文件定位。

### 帧提取限制

| Option | Description | Selected |
|--------|-------------|----------|
| frame_load_cap=16（推荐） | 默认 16 帧，用户可调，防止 OOM | ✓ |
| 不限（全部帧） | 提取全部帧，可能 OOM | |
| Claude 你决定 | Claude 自行决定 | |

**User's choice:** frame_load_cap=16（推荐）
**Notes:** 4 秒视频约 96 帧，16 帧约 1.5 帧/秒。合理预览。

---

## 图片转换细节

| Option | Description | Selected |
|--------|-------------|----------|
| JPEG quality=95（推荐） | CLAUDE.md 推荐，质量与大小平衡 | ✓ |
| JPEG quality=100 | 无压缩损失，文件更大 | |
| Claude 你决定 | Claude 自行决定 | |

**User's choice:** JPEG quality=95（推荐）
**Notes:** 与 CLAUDE.md 技术栈推荐一致。

---

## Claude's Discretion

- api_client.py I2V 扩展方式（新增函数 vs 扩展现有函数）
- 视频下载实现细节（requests streaming）
- 帧提取实现（opencv）
- 文件命名策略
- 子文件夹处理
- I2V 节点参数布局

## Deferred Ideas

None — discussion stayed within phase scope.

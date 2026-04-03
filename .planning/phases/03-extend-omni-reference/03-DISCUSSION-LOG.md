# Phase 3: Extend + Omni Reference - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 03-extend-omni-reference
**Areas discussed:** API 兼容性验证, 输出格式冲突, Omni 多图输入设计, Omni 提示词格式

---

## API 兼容性验证

| Option | Description | Selected |
|--------|-------------|----------|
| 先验证再实现 | Phase 3 第一个任务是 API 验证。确认 payload 格式后再构建节点。不可用的功能移出本阶段。 | ✓ |
| 边实现边验证 | 先按参考项目 payload 开发，后续调整 | |
| 暂缓整个 Phase 3 | 先做 Phase 4，等 API 文档明确后回来 | |

**User's choice:** 先验证再实现（推荐）
**Notes:** AIHubMix 文档未明确记录 Extend/Omni 端点。需要用 seedance_video.py 测试脚本实际验证。

---

## 输出格式冲突

| Option | Description | Selected |
|--------|-------------|----------|
| 沿用现有模式 | Extend/Omni 只输出 (video_url, video_id)。first_frame 由 Save Video 处理。 | ✓ |
| 按需求文档改 | 输出 (video_url, first_frame, video_id)，与其他节点不一致 | |
| 统一改为含 first_frame | 所有节点都加 first_frame，需回改 Phase 1/2 | |

**User's choice:** 沿用现有模式（推荐）
**Notes:** 需求文档 EXTD-02/OMNI-03 中 first_frame (IMAGE) 输出不实施。与 D-01/D-10/D-11 保持一致。

---

## Omni 多图输入设计

| Option | Description | Selected |
|--------|-------------|----------|
| 固定插槽 | 9 个 IMAGE + 3 个 STRING（video URL）可选输入。未连接自动忽略。 | ✓ |
| Batch tensor | 1 个 IMAGE 输入接受 batch，要求同尺寸 | |
| 多个节点变体 | 不同数量输入的多个节点 | |

**User's choice:** 固定插槽（推荐）
**Notes:** 节点会比较大，但直观。使用 ComfyUI optional 输入块。

---

## Omni 提示词格式

| Option | Description | Selected |
|--------|-------------|----------|
| 验证时确认 | 在 API 验证阶段一起确认。先按 MuAPI @image1/@video1 占位符格式假设。 | ✓ |
| 无需占位符 | 图片/视频在 payload 中单独传递，提示词纯文本 | |
| 占位符仅供参考 | 保留占位符给用户看，实际发送时去掉 | |

**User's choice:** 验证时确认（推荐）
**Notes:** 取决于 AIHubMix API 实际支持的 payload 格式。

---

## Claude's Discretion

- Extend 节点参数布局
- Omni 节点输入命名（image_1..9, video_url_1..3）
- API client 函数命名
- API 验证测试脚本实现
- 错误消息中文措辞

## Deferred Ideas

None — discussion stayed within phase scope.

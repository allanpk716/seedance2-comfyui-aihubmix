# Phase 1: Foundation + Text-to-Video - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 01-foundation-text-to-video
**Areas discussed:** T2V 输出策略, 进度反馈, API Key 节点 UX, 错误消息风格

---

## T2V 输出策略

| Option | Description | Selected |
|--------|-------------|----------|
| T2V 内部下载 | T2V 节点下载视频、提取第一帧、返回 IMAGE tensor | |
| 推迟到 Save Video 节点 | T2V 只输出 video_url + video_id，first_frame 留到 Phase 2 | ✓ |
| 尝试获取缩略图 | 从 API 响应获取缩略图 URL（不确定 AIHubMix 是否支持） | |

**User's choice:** 推迟到 Save Video 节点
**Notes:** 简化 Phase 1 范围。T2V 输出 video_url (STRING) + video_id (STRING)。

---

## 进度反馈

| Option | Description | Selected |
|--------|-------------|----------|
| 控制台日志 | ComfyUI 控制台/终端显示轮询进度（print 输出） | ✓ |
| 静默运行 | 静默轮询，只在完成时打印结果 | |
| ComfyUI 进度条 | 用 PromptServer API 推送进度到 Web UI | |

**User's choice:** 控制台日志（推荐）
**Notes:** 简单直接，和参考项目一致。用 print 输出到 ComfyUI 日志窗口。

---

## API Key 节点 UX

| Option | Description | Selected |
|--------|-------------|----------|
| 简单传递 | 字符串输入 + 传递，和参考项目一致 | ✓ |
| 带格式验证 | 验证 key 格式（sk- 前缀、长度等） | |
| 你来决定 | Claude 决定 | |

**User's choice:** 简单传递（推荐）
**Notes:** T2V 节点有可选 api_key 字段作为备选。不做验证或掩码。

---

## 错误消息风格

| Option | Description | Selected |
|--------|-------------|----------|
| 详细 + 建议 | 显示 API 错误 + 可操作建议 | ✓ |
| 仅传递 API 错误 | 只显示 API 返回的错误信息 | |

**User's choice:** 详细 + 建议（推荐）
**Notes:** 错误消息用中文，包含技术细节（状态码）和可操作建议。

---

## Claude's Discretion

- 文件/模块结构和命名
- API 客户端实现细节
- SIZE_MAP 数据结构
- 节点参数定义
- 轮询间隔

## Deferred Ideas

无 — 讨论均在阶段范围内。

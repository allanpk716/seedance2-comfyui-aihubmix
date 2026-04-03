# Phase 3: Extend + Omni Reference - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning (pending API verification)

<domain>
## Phase Boundary

Video Extend node (extend a previously generated video using video_id + optional continuation prompt) and Omni Reference node (combine multiple images, video URLs, and prompt for multi-modal generation). Both use AIHubMix API.

This phase does NOT include: T2V, I2V, Save Video, GitHub publishing, or Character features.

**Critical prerequisite:** API verification must pass before node implementation begins (D-14).

</domain>

<decisions>
## Implementation Decisions

### API Verification Strategy
- **D-14:** API 验证优先 — 先用 `seedance_video.py` 测试脚本验证 Extend/Omni 的 payload 格式和 AIHubMix API 兼容性。确认可行后再构建节点。不可用的功能移出本阶段。
  - AIHubMix 文档未明确记录 Extend/Omni 端点格式，需要实际测试验证。
  - 参考项目使用 MuAPI 的独立端点（`/api/v1/seedance-v2.0-extend`、`/api/v1/seedance-2.0-omni-reference`），但 AIHubMix 用统一的 `POST /v1/videos`。
  - Extend 可能在 payload 中加 `request_id` 或类似字段引用前次生成的视频。
  - Omni 可能在 payload 中加图片/视频数组字段。

### Output Format
- **D-15:** Extend/Omni 节点沿用现有输出格式 `(video_url: STRING, video_id: STRING)`，与 T2V/I2V 保持一致。first_frame 继续由 Save Video 节点处理。
  - 需求文档 EXTD-02/OMNI-03 中 first_frame (IMAGE) 输出不实施，与 D-01/D-10/D-11 一致。

### Omni Reference Input Design
- **D-16:** Omni Reference 使用固定插槽 — 9 个可选 IMAGE 输入 + 3 个可选 STRING 输入（video URL）。未连接的槽自动忽略。
  - 使用 ComfyUI optional 输入块，和 I2V 的 `api_key` optional 模式一致。
  - 节点会比较大，但直观易用。

### Omni Prompt Format
- **D-17:** Omni 提示词格式（是否需要 @image1/@video1 占位符）在 API 验证阶段确认。先按 MuAPI 的占位符格式假设。

### Claude's Discretion
- Extend 节点的参数布局（video_id 输入 + 可选 prompt + 生成参数）
- Omni 节点的 9+3 输入命名（image_1..image_9, video_url_1..video_url_3）
- API client 新增函数的具体命名（create_extend_video / create_omni_video 等）
- API 验证测试脚本的具体实现
- 错误消息措辞（遵循 D-08 中文风格）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### API Reference
- `seedance_video.py` — 测试脚本，用于 API 验证。需扩展以支持 Extend/Omni 的 payload 测试。
- `api_client.py` — 现有 API 客户端。需 EXTEND（非重写）以添加 Extend/Omni 函数。复用 `_get_headers`、`_get_size`、`_check_response`、`wait_for_video`、`SIZE_MAP`。

### Existing Implementation
- `nodes.py` — 节点模板。`SeedanceTextToVideo`（简单生成参数）、`SeedanceImageToVideo`（IMAGE 输入 + 转换逻辑）。
- `__init__.py` — 需更新以注册 Extend/Omni 节点。
- `tests/conftest.py` — 共享测试 fixtures。

### Reference Project (MuAPI - payload format reference only)
- https://github.com/Anil-matcha/seedance2-comfyui `seedance2_nodes.py` — `Seedance2Extend` class（`request_id` + `prompt` + `duration` + `quality`）、`Seedance2Omni` class（`prompt` + `images_list` + `video_files` + `audio_files`）。
- 注意：MuAPI 用独立端点，AIHubMix 用统一端点，payload 格式可能不同。

### External API Docs
- AIHubMix Video Gen API: https://docs.aihubmix.com/en/api/Video-Gen — 仅记录 T2V/I2V，Extend/Omni 未显式记录。
- Model ID: `doubao-seedance-2-0-260128`

### ComfyUI Reference
- ComfyUI Custom Node Walkthrough: https://docs.comfy.org/custom-nodes/walkthrough
- ComfyUI Tensors: https://docs.comfy.org/custom-nodes/backend/tensors — IMAGE format [B,H,W,C] float32

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `api_client.py` `_get_headers`, `_get_size`, `_check_response`, `wait_for_video`, `SIZE_MAP` — Extend/Omni 函数可直接复用。
- `nodes.py` `SeedanceImageToVideo` — IMAGE tensor → base64 转换逻辑可复用于 Omni 的多图输入。
- `nodes.py` optional 输入模式 — Omni 的 9+3 可选输入可用同样模式。

### Established Patterns
- Function-based API client（非 class） — per Phase 1
- Node CATEGORY = "Seedance 2.0" — 所有节点统一
- @classmethod INPUT_TYPES, RETURN_TYPES tuple, FUNCTION string — ComfyUI 标准模式
- API key validation: `if not api_key: raise ValueError(...)` — 统一错误处理
- 错误消息中文 — per D-08
- SIZE_MAP 复用 — per Phase 1

### Integration Points
- `__init__.py`: 注册 `SeedanceExtendVideo` 和 `SeedanceOmniReference` 到 NODE_CLASS_MAPPINGS / NODE_DISPLAY_NAME_MAPPINGS
- `api_client.py`: 添加 `create_extend_video`/`create_and_wait_extend` 和 `create_omni_video`/`create_and_wait_omni` 函数
- `nodes.py`: 添加两个新节点类，import 新 API 函数

</code_context>

<specifics>
## Specific Ideas

- Extend 节点接受 video_id（STRING，从前次生成节点连线）+ 可选 prompt（续写描述）
- Omni 节点的 9 个图片输入和 I2V 一样做 base64 转换（D-13 模式）
- API 验证应作为 Phase 3 第一个 plan，节点实现在验证通过后再开始
- 如果 AIHubMix 不支持 Extend 或 Omni，该功能移出本阶段

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-extend-omni-reference*
*Context gathered: 2026-04-03*

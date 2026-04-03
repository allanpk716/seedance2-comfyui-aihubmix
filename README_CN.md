# Seedance 2.0 ComfyUI 插件

[English](./README.md) | 中文

基于 AIHubMix API 的 Seedance 2.0 AI 视频生成 ComfyUI 自定义节点。通过文本提示词、图片或续写已有视频，在 ComfyUI 中直接生成视频。

## 功能特性

- **文生视频 (Text-to-Video)** -- 通过文本提示词生成视频，支持自定义分辨率和时长
- **图生视频 (Image-to-Video)** -- 将参考图片配合文本提示词生成视频
- **视频续写 (Video Extend)** -- 续写已生成的视频，可选添加续写提示词
- **全能参考 (Omni Reference)** -- 组合多张图片和视频链接进行多模态生成
- **保存视频 (Save Video)** -- 下载生成的视频，提取帧画面，在 ComfyUI 画布上预览

## 安装

### 方法一：ComfyUI Manager（推荐）

1. 打开 ComfyUI Manager
2. 点击 **"Install via Git URL"**
3. 输入：`https://github.com/<your-github-username>/seedance2-comfyui-aihubmix`
4. 点击 **Install**，然后重启 ComfyUI

### 方法二：手动安装

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/<your-github-username>/seedance2-comfyui-aihubmix.git
pip install -r seedance2-comfyui-aihubmix/requirements.txt
```

安装后重启 ComfyUI。

## 快速开始

1. 前往 [AIHubMix](https://aihubmix.com) 获取你的 API Key
2. 安装插件（见上方安装说明）
3. 在 ComfyUI 中添加 **"Seedance 2.0 API Key"** 节点，粘贴你的 API Key
4. 添加任意生成节点，连接 API Key，输入提示词，运行即可

## 节点参考

所有生成节点均接受 `api_key` 作为可选输入（从 API Key 节点连线或直接填写）。模型：`doubao-seedance-2-0-260128`。

| 节点 | 主要输入 | 输出 |
|------|---------|------|
| **Seedance 2.0 API Key** | api_key (STRING) | api_key (STRING) |
| **Seedance 2.0 Text to Video** | prompt (STRING, 必填), duration (4-15秒), resolution (480p/720p/1080p), ratio (6种选项) | video_url (STRING), video_id (STRING) |
| **Seedance 2.0 Image to Video** | image (IMAGE, 必填), prompt (STRING, 必填), duration, resolution, ratio | video_url (STRING), video_id (STRING) |
| **Seedance 2.0 Video Extend** | video_id (STRING, 必填), prompt (STRING), duration, resolution, ratio | video_url (STRING), video_id (STRING) |
| **Seedance 2.0 Omni Reference** | prompt (STRING, 必填), image_1..image_9 (IMAGE), video_url_1..video_url_3 (STRING), duration, resolution, ratio | video_url (STRING), video_id (STRING) |
| **Seedance 2.0 Save Video** | video_url (STRING, 必填), filename_prefix, subfolder, frame_load_cap (1-1000) | frames (IMAGE), first_frame_path (STRING), video_path (STRING) |

### 支持的分辨率和比例

| 分辨率 | 可用比例 |
|-------|---------|
| 480p | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 |
| 720p | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 |
| 1080p | 使用 API 默认尺寸 |

## 示例工作流

### 文生视频工作流

1. 添加 **"Seedance 2.0 API Key"** 节点 -- 粘贴你的 AIHubMix API Key
2. 添加 **"Seedance 2.0 Text to Video"** 节点 -- 输入提示词，设置分辨率和时长
3. 将 API Key 节点的输出连接到 T2V 节点的 `api_key` 输入
4. 添加 **"Seedance 2.0 Save Video"** 节点
5. 将 T2V 的 `video_url` 输出连接到 Save Video 节点的 `video_url` 输入
6. 点击 **"Queue Prompt"** 开始生成

### 图生视频工作流

1. 添加 **"Seedance 2.0 API Key"** 节点 -- 粘贴你的 AIHubMix API Key
2. 添加 **"Load Image"** 节点（ComfyUI 内置）-- 选择参考图片
3. 添加 **"Seedance 2.0 Image to Video"** 节点 -- 输入提示词，设置分辨率和时长
4. 将 API Key 输出连接到 I2V 的 `api_key` 输入
5. 将 Load Image 的 `IMAGE` 输出连接到 I2V 的 `image` 输入
6. 添加 **"Seedance 2.0 Save Video"** 节点
7. 将 I2V 的 `video_url` 输出连接到 Save Video 节点的 `video_url` 输入
8. 点击 **"Queue Prompt"** 开始生成

## 常见问题

**如何获取 API Key？**
前往 [AIHubMix](https://aihubmix.com) 注册账号，进入 Dashboard > API Keys，创建新的 API Key。

**支持哪些分辨率？**
480p、720p 和 1080p。可用比例：16:9、9:16、4:3、3:4、1:1、21:9。注意：1080p 使用 API 默认尺寸。

**视频最长可以多少秒？**
4 到 15 秒，默认 5 秒。

**出现 401 错误：**
请检查 API Key 是否正确。可在 aihubmix.com 查看和管理你的 Key。

**出现 402 错误：**
账户余额不足，请到 aihubmix.com 充值。

**出现 429 错误：**
请求过于频繁，请稍后重试。

**安装后节点没有出现：**
完全重启 ComfyUI，检查 ComfyUI 控制台是否有导入错误。

## 环境要求

- Python >= 3.8
- ComfyUI
- 依赖（大部分已随 ComfyUI 安装）：
  - requests >= 2.28
  - Pillow >= 9.0
  - numpy >= 1.23
  - opencv-python >= 4.7

## 许可证

MIT License。详见 [LICENSE](./LICENSE)。

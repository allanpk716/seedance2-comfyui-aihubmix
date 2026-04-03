# Seedance 2.0 ComfyUI Plugin

English | [中文](./README_CN.md)

ComfyUI custom nodes for Seedance 2.0 AI video generation via AIHubMix API. Generate videos from text prompts, images, or extend existing videos -- all inside ComfyUI.

## Features

- **Text-to-Video** -- Generate videos from text prompts with configurable resolution and duration
- **Image-to-Video** -- Animate reference images into videos with a text prompt
- **Video Extend** -- Continue previously generated videos with an optional continuation prompt
- **Omni Reference** -- Combine multiple images and video URLs for multi-modal generation
- **Save Video** -- Download generated videos, extract frames, and preview on the ComfyUI canvas

## Installation

### Method 1: ComfyUI Manager (Recommended)

1. Open ComfyUI Manager
2. Click **"Install via Git URL"**
3. Enter: `https://github.com/<your-github-username>/seedance2-comfyui-aihubmix`
4. Click **Install**, then restart ComfyUI

### Method 2: Manual Install

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/<your-github-username>/seedance2-comfyui-aihubmix.git
pip install -r seedance2-comfyui-aihubmix/requirements.txt
```

Restart ComfyUI after installation.

## Quick Start

1. Get your API key from [AIHubMix](https://aihubmix.com)
2. Install the plugin (see Installation above)
3. In ComfyUI, add a **"Seedance 2.0 API Key"** node and paste your key
4. Add any generation node, connect the API key, enter a prompt, and run

## Node Reference

All generation nodes accept `api_key` as an optional input (wire from the API Key node or fill in directly). Model: `doubao-seedance-2-0-260128`.

| Node | Key Inputs | Outputs |
|------|-----------|---------|
| **Seedance 2.0 API Key** | api_key (STRING) | api_key (STRING) |
| **Seedance 2.0 Text to Video** | prompt (STRING, required), duration (4-15s), resolution (480p/720p/1080p), ratio (6 options) | video_url (STRING), video_id (STRING) |
| **Seedance 2.0 Image to Video** | image (IMAGE, required), prompt (STRING, required), duration, resolution, ratio | video_url (STRING), video_id (STRING) |
| **Seedance 2.0 Video Extend** | video_id (STRING, required), prompt (STRING), duration, resolution, ratio | video_url (STRING), video_id (STRING) |
| **Seedance 2.0 Omni Reference** | prompt (STRING, required), image_1..image_9 (IMAGE), video_url_1..video_url_3 (STRING), duration, resolution, ratio | video_url (STRING), video_id (STRING) |
| **Seedance 2.0 Save Video** | video_url (STRING, required), filename_prefix, subfolder, frame_load_cap (1-1000) | frames (IMAGE), first_frame_path (STRING), video_path (STRING) |

### Supported Resolutions and Ratios

| Resolution | Available Ratios |
|-----------|-----------------|
| 480p | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 |
| 720p | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 |
| 1080p | Uses API default size |

## Example Workflows

### Text-to-Video Workflow

1. Add **"Seedance 2.0 API Key"** node -- paste your AIHubMix API key
2. Add **"Seedance 2.0 Text to Video"** node -- enter your prompt, set resolution and duration
3. Connect API Key node output to T2V node `api_key` input
4. Add **"Seedance 2.0 Save Video"** node
5. Connect T2V `video_url` output to Save Video node `video_url` input
6. Click **"Queue Prompt"** to generate

### Image-to-Video Workflow

1. Add **"Seedance 2.0 API Key"** node -- paste your AIHubMix API key
2. Add a **"Load Image"** node (built-in ComfyUI) -- select your reference image
3. Add **"Seedance 2.0 Image to Video"** node -- enter your prompt, set resolution and duration
4. Connect API Key output to I2V `api_key` input
5. Connect Load Image `IMAGE` output to I2V `image` input
6. Add **"Seedance 2.0 Save Video"** node
7. Connect I2V `video_url` output to Save Video node `video_url` input
8. Click **"Queue Prompt"** to generate

## FAQ

**How do I get an API key?**
Sign up at [AIHubMix](https://aihubmix.com), go to Dashboard > API Keys, and create a new key.

**What resolutions are supported?**
480p, 720p, and 1080p. Available aspect ratios: 16:9, 9:16, 4:3, 3:4, 1:1, 21:9. Note: 1080p uses API defaults for size.

**How long can videos be?**
4 to 15 seconds. Default is 5 seconds.

**I get a 401 error:**
Check that your API key is correct. You can view and manage your keys at aihubmix.com.

**I get a 402 error:**
Your account balance is insufficient. Top up at aihubmix.com.

**I get a 429 error:**
Too many requests. Wait a moment and try again.

**Nodes don't appear after install:**
Restart ComfyUI completely. Check the ComfyUI console for any import errors.

## Requirements

- Python >= 3.8
- ComfyUI
- Dependencies (most already installed with ComfyUI):
  - requests >= 2.28
  - Pillow >= 9.0
  - numpy >= 1.23
  - opencv-python >= 4.7

## License

MIT License. See [LICENSE](./LICENSE) for details.

"""AIHubMix API client for Seedance 2.0 video generation.

Encapsulates all HTTP communication with AIHubMix so ComfyUI nodes
never call requests directly.
"""
import time

import requests

BASE_URL = "https://aihubmix.com/v1"
MODEL = "doubao-seedance-2-0-260128"

SIZE_MAP = {
    ("480p", "16:9"): "832x480",
    ("480p", "9:16"): "480x832",
    ("480p", "1:1"):  "624x624",
    ("480p", "4:3"):  "640x480",
    ("480p", "3:4"):  "480x640",
    ("480p", "21:9"): "1120x480",
    ("720p", "16:9"): "1280x720",
    ("720p", "9:16"): "720x1280",
    ("720p", "1:1"):  "960x960",
    ("720p", "4:3"):  "960x720",
    ("720p", "3:4"):  "720x960",
    ("720p", "21:9"): "1680x720",
}


def _get_headers(api_key):
    """Return HTTP headers with Bearer auth."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _get_size(resolution, ratio):
    """Return size string for the given resolution/ratio, or None for 1080p (API default)."""
    if resolution == "1080p":
        return None
    return SIZE_MAP.get((resolution, ratio))


def _check_response(resp):
    """Raise descriptive errors for common API failures.

    Uses Chinese error messages per D-08 for actionable user guidance.
    """
    if resp.status_code == 200:
        return
    if resp.status_code == 401:
        raise RuntimeError(
            "认证失败 (401)：请检查你的 API 密钥是否正确，可在 aihubmix.com 查看"
        )
    if resp.status_code == 402:
        raise RuntimeError(
            "余额不足 (402)：请到 aihubmix.com 充值"
        )
    if resp.status_code == 429:
        raise RuntimeError(
            "请求过于频繁 (429)：请稍后重试"
        )
    resp.raise_for_status()


def create_video(api_key, prompt, duration=5, resolution="1080p", ratio="16:9"):
    """Submit a video generation task to AIHubMix. Returns the video ID string."""
    headers = _get_headers(api_key)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "seconds": duration,
    }

    size = _get_size(resolution, ratio)
    if size:
        payload["size"] = size

    resp = requests.post(f"{BASE_URL}/videos", headers=headers, json=payload)
    _check_response(resp)

    data = resp.json()
    video_id = data.get("id") or data.get("video_id")
    if not video_id:
        raise RuntimeError(f"No video ID in response: {data}")

    return video_id


def wait_for_video(api_key, video_id, poll_interval=5, max_wait=600):
    """Poll GET /v1/videos/{video_id} until completed, failed, or timeout.

    Prints progress updates to console per D-03/D-04.
    Catches network errors and retries per APIC-04.
    """
    headers = _get_headers(api_key)
    status = "queued"
    progress = 0
    elapsed = 0
    data = {}

    while status in ("in_progress", "queued") and elapsed < max_wait:
        try:
            resp = requests.get(f"{BASE_URL}/videos/{video_id}", headers=headers)
            if resp.status_code != 200:
                print(f"[Seedance] Status check error ({resp.status_code}), retrying...")
                time.sleep(poll_interval)
                elapsed += poll_interval
                continue

            data = resp.json()
            status = data.get("status", status)
            progress = data.get("progress", progress) or 0
            print(f"[Seedance] {status} - {progress}%")
        except requests.RequestException as e:
            print(f"[Seedance] Network error: {e}, retrying...")

        time.sleep(poll_interval)
        elapsed += poll_interval

    if status == "failed":
        error_msg = "Unknown error"
        error_data = data.get("error")
        if isinstance(error_data, dict):
            error_msg = error_data.get("message", error_msg)
        elif isinstance(error_data, str):
            error_msg = error_data
        raise RuntimeError(f"Video generation failed: {error_msg}")

    if status != "completed":
        raise RuntimeError(
            f"Video generation timed out after {max_wait}s (status: {status})"
        )

    return data


def create_i2v_video(api_key, prompt, image_data_uri, duration=5, resolution="1080p", ratio="16:9"):
    """Submit an I2V task with image reference. Returns video ID string."""
    headers = _get_headers(api_key)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "seconds": duration,
        "input": image_data_uri,
    }

    size = _get_size(resolution, ratio)
    if size:
        payload["size"] = size

    resp = requests.post(f"{BASE_URL}/videos", headers=headers, json=payload)
    _check_response(resp)

    data = resp.json()
    video_id = data.get("id") or data.get("video_id")
    if not video_id:
        raise RuntimeError(f"No video ID in response: {data}")

    return video_id


def create_and_wait_i2v(api_key, prompt, image_data_uri, duration=5, resolution="1080p", ratio="16:9"):
    """Create I2V video and wait for completion. Returns result dict with video_url and video_id."""
    video_id = create_i2v_video(api_key, prompt, image_data_uri, duration, resolution, ratio)
    print(f"[Seedance] I2V video created: {video_id}")

    result = wait_for_video(api_key, video_id)
    print(f"[Seedance] I2V video completed: {result.get('video_url', 'N/A')}")

    video_url = result.get("video_url") or result.get("url", "")
    return {
        "video_url": video_url,
        "video_id": video_id,
    }


def create_extend_video(api_key, video_id, prompt="", duration=5, resolution="1080p", ratio="16:9"):
    """Submit a video extend task referencing a previous video_id. Returns the new video ID string."""
    headers = _get_headers(api_key)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "seconds": duration,
        "request_id": video_id,
    }

    size = _get_size(resolution, ratio)
    if size:
        payload["size"] = size

    resp = requests.post(f"{BASE_URL}/videos", headers=headers, json=payload)
    _check_response(resp)

    data = resp.json()
    new_video_id = data.get("id") or data.get("video_id")
    if not new_video_id:
        raise RuntimeError(f"No video ID in response: {data}")

    return new_video_id


def create_and_wait_extend(api_key, video_id, prompt="", duration=5, resolution="1080p", ratio="16:9"):
    """Create extend video and wait for completion. Returns result dict with video_url and video_id."""
    new_video_id = create_extend_video(api_key, video_id, prompt, duration, resolution, ratio)
    print(f"[Seedance] Extend video created: {new_video_id}")

    result = wait_for_video(api_key, new_video_id)
    print(f"[Seedance] Extend video completed: {result.get('video_url', 'N/A')}")

    video_url = result.get("video_url") or result.get("url", "")
    return {
        "video_url": video_url,
        "video_id": new_video_id,
    }


def create_and_wait(api_key, prompt, duration=5, resolution="1080p", ratio="16:9"):
    """Create a video and wait for completion. Returns result dict with video_url and video_id."""
    video_id = create_video(api_key, prompt, duration, resolution, ratio)
    print(f"[Seedance] Video created: {video_id}")

    result = wait_for_video(api_key, video_id)
    print(f"[Seedance] Video completed: {result.get('video_url', 'N/A')}")

    video_url = result.get("video_url") or result.get("url", "")
    return {
        "video_url": video_url,
        "video_id": video_id,
    }

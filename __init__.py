from .nodes import SeedanceApiKey, SeedanceTextToVideo, SeedanceImageToVideo, SeedanceSaveVideo

NODE_CLASS_MAPPINGS = {
    "SeedanceApiKey": SeedanceApiKey,
    "SeedanceTextToVideo": SeedanceTextToVideo,
    "SeedanceImageToVideo": SeedanceImageToVideo,
    "SeedanceSaveVideo": SeedanceSaveVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeedanceApiKey": "Seedance 2.0 API Key",
    "SeedanceTextToVideo": "Seedance 2.0 Text to Video",
    "SeedanceImageToVideo": "Seedance 2.0 Image to Video",
    "SeedanceSaveVideo": "Seedance 2.0 Save Video",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

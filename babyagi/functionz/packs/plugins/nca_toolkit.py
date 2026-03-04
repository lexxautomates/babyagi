# NCA Toolkit Plugin for BabyAGI
# Integrates No-Code Architects Toolkit media processing capabilities
# Repository: https://github.com/lexxautomates/no-code-architects-toolkit

import requests
from typing import Optional, Dict, Any, List

# Base URL for NCA Toolkit API (deployed on VPS)
NCA_BASE_URL = "http://31.220.20.251:8090"
# MinIO S3 storage URL for accessing processed files
MINIO_URL = "http://31.220.20.251:9000"

def _get_headers():
    """Get headers with API key for NCA Toolkit authentication."""
    api_key = globals().get('nca_api_key', 'nca_babyagi_integration_2024')
    return {"X-API-Key": api_key, "Content-Type": "application/json"}

# ============================================================
# VIDEO PROCESSING FUNCTIONS
# ============================================================

@func.register_function(
    metadata={"description": "Add captions/subtitles to a video file."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "video_url", "type": "str", "description": "URL of the video file"},
        {"name": "captions", "type": "str", "description": "Caption text or SRT file URL"},
        {"name": "position", "type": "str", "description": "Caption position: bottom, top, center"},
        {"name": "font_size", "type": "int", "description": "Font size for captions"}
    ]
)
def nca_add_video_captions(
    video_url: str, 
    captions: str, 
    position: str = "bottom", 
    font_size: int = 24
) -> Dict[str, Any]:
    """
    Add captions to a video using NCA Toolkit.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/video/caption",
        headers=_get_headers(),
        json={
            "video_url": video_url,
            "captions": captions,
            "position": position,
            "font_size": font_size
        }
    )
    return response.json()


@func.register_function(
    metadata={"description": "Concatenate multiple videos into a single video."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "video_urls", "type": "list", "description": "List of video URLs to concatenate"},
        {"name": "output_format", "type": "str", "description": "Output format: mp4, webm, mov"}
    ]
)
def nca_concatenate_videos(
    video_urls: List[str], 
    output_format: str = "mp4"
) -> Dict[str, Any]:
    """
    Concatenate multiple videos into one using NCA Toolkit.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/video/concatenate",
        headers=_get_headers(),
        json={
            "video_urls": video_urls,
            "output_format": output_format
        }
    )
    return response.json()


@func.register_function(
    metadata={"description": "Extract a thumbnail/image from a video at a specific timestamp."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "video_url", "type": "str", "description": "URL of the video file"},
        {"name": "timestamp", "type": "str", "description": "Timestamp for thumbnail (e.g., '00:00:05')"}
    ]
)
def nca_extract_video_thumbnail(
    video_url: str, 
    timestamp: str = "00:00:00"
) -> Dict[str, Any]:
    """
    Extract a thumbnail from a video at the specified timestamp.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/video/thumbnail",
        headers=_get_headers(),
        json={
            "video_url": video_url,
            "timestamp": timestamp
        }
    )
    return response.json()


@func.register_function(
    metadata={"description": "Cut/trim a video between start and end times."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "video_url", "type": "str", "description": "URL of the video file"},
        {"name": "start_time", "type": "str", "description": "Start time (e.g., '00:00:10')"},
        {"name": "end_time", "type": "str", "description": "End time (e.g., '00:00:30')"}
    ]
)
def nca_cut_video(
    video_url: str, 
    start_time: str = "00:00:00",
    end_time: str = "00:00:10"
) -> Dict[str, Any]:
    """
    Cut/trim a video between specified times.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/video/cut",
        headers=_get_headers(),
        json={
            "video_url": video_url,
            "start_time": start_time,
            "end_time": end_time
        }
    )
    return response.json()


@func.register_function(
    metadata={"description": "Trim video from a start time to end."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "video_url", "type": "str", "description": "URL of the video file"},
        {"name": "start_time", "type": "str", "description": "Start time (e.g., '00:00:10')"},
        {"name": "duration", "type": "str", "description": "Duration to trim (e.g., '10')"}
    ]
)
def nca_trim_video(
    video_url: str, 
    start_time: str = "00:00:00",
    duration: str = "10"
) -> Dict[str, Any]:
    """
    Trim a video from start time for specified duration.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/video/trim",
        headers=_get_headers(),
        json={
            "video_url": video_url,
            "start_time": start_time,
            "duration": duration
        }
    )
    return response.json()


@func.register_function(
    metadata={"description": "Split a video into multiple parts."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "video_url", "type": "str", "description": "URL of the video file"},
        {"name": "split_points", "type": "list", "description": "List of timestamps to split at"}
    ]
)
def nca_split_video(
    video_url: str, 
    split_points: List[str] = None
) -> Dict[str, Any]:
    """
    Split a video into multiple parts at specified timestamps.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/video/split",
        headers=_get_headers(),
        json={
            "video_url": video_url,
            "split_points": split_points or ["00:00:10"]
        }
    )
    return response.json()


# ============================================================
# AUDIO PROCESSING FUNCTIONS
# ============================================================

@func.register_function(
    metadata={"description": "Transcribe audio/video to text using Whisper."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "media_url", "type": "str", "description": "URL of the audio/video file"},
        {"name": "language", "type": "str", "description": "Language code (e.g., 'en', 'es')"}
    ]
)
def nca_transcribe_media(
    media_url: str, 
    language: str = "en"
) -> Dict[str, Any]:
    """
    Transcribe audio or video to text using NCA Toolkit's Whisper integration.
    Replaces paid Whisper API with free self-hosted version.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/media/transcribe",
        headers=_get_headers(),
        json={
            "media_url": media_url,
            "language": language
        }
    )
    return response.json()


@func.register_function(
    metadata={"description": "Convert audio/video file to MP3 format."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "media_url", "type": "str", "description": "URL of the audio/video file"}
    ]
)
def nca_convert_to_mp3(media_url: str) -> Dict[str, Any]:
    """
    Convert audio or video to MP3 format.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/media/convert/mp3",
        headers=_get_headers(),
        json={"media_url": media_url}
    )
    return response.json()


@func.register_function(
    metadata={"description": "Convert media file to different format."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "media_url", "type": "str", "description": "URL of the media file"},
        {"name": "output_format", "type": "str", "description": "Output format: mp3, mp4, wav, webm"}
    ]
)
def nca_convert_media(
    media_url: str, 
    output_format: str = "mp3"
) -> Dict[str, Any]:
    """
    Convert media to different format.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/media/convert",
        headers=_get_headers(),
        json={
            "media_url": media_url,
            "output_format": output_format
        }
    )
    return response.json()


@func.register_function(
    metadata={"description": "Concatenate multiple audio files into one."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "audio_urls", "type": "list", "description": "List of audio URLs to concatenate"}
    ]
)
def nca_concatenate_audio(audio_urls: List[str]) -> Dict[str, Any]:
    """
    Concatenate multiple audio files.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/audio/concatenate",
        headers=_get_headers(),
        json={"audio_urls": audio_urls}
    )
    return response.json()


# ============================================================
# IMAGE PROCESSING FUNCTIONS
# ============================================================

@func.register_function(
    metadata={"description": "Take a screenshot of a webpage."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "url", "type": "str", "description": "URL of the webpage to screenshot"},
        {"name": "full_page", "type": "bool", "description": "Capture full page or viewport"},
        {"name": "width", "type": "int", "description": "Viewport width in pixels"},
        {"name": "height", "type": "int", "description": "Viewport height in pixels"}
    ]
)
def nca_webpage_screenshot(
    url: str, 
    full_page: bool = True, 
    width: int = 1920, 
    height: int = 1080
) -> Dict[str, Any]:
    """
    Take a screenshot of a webpage using NCA Toolkit.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/image/screenshot/webpage",
        headers=_get_headers(),
        json={
            "url": url,
            "full_page": full_page,
            "width": width,
            "height": height
        }
    )
    return response.json()


@func.register_function(
    metadata={"description": "Convert image to video with optional effects."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "image_url", "type": "str", "description": "URL of the image"},
        {"name": "duration", "type": "int", "description": "Duration in seconds"},
        {"name": "effect", "type": "str", "description": "Effect: zoom, pan, fade"}
    ]
)
def nca_image_to_video(
    image_url: str, 
    duration: int = 5, 
    effect: str = "zoom"
) -> Dict[str, Any]:
    """
    Convert an image to video with effects.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/image/convert/video",
        headers=_get_headers(),
        json={
            "image_url": image_url,
            "duration": duration,
            "effect": effect
        }
    )
    return response.json()


# ============================================================
# MEDIA DOWNLOAD FUNCTIONS
# ============================================================

@func.register_function(
    metadata={"description": "Download video/audio from various platforms using yt-dlp."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "media_url", "type": "str", "description": "URL of the media to download"},
        {"name": "audio_extract", "type": "bool", "description": "Extract audio only"},
        {"name": "audio_format", "type": "str", "description": "Audio format: mp3, wav, aac"}
    ]
)
def nca_download_media(
    media_url: str, 
    audio_extract: bool = False,
    audio_format: str = "mp3"
) -> Dict[str, Any]:
    """
    Download media from YouTube, TikTok, Instagram, Twitter, etc. using yt-dlp.
    Supports 1000+ platforms.
    """
    payload = {
        "media_url": media_url,
        "cloud_upload": False
    }
    
    if audio_extract:
        payload["audio"] = {
            "extract": True,
            "format": audio_format
        }
    
    response = requests.post(
        f"{NCA_BASE_URL}/v1/BETA/media/download",
        headers=_get_headers(),
        json=payload
    )
    return response.json()


@func.register_function(
    metadata={"description": "Get metadata for a media file."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "media_url", "type": "str", "description": "URL of the media file"}
    ]
)
def nca_get_media_metadata(media_url: str) -> Dict[str, Any]:
    """
    Get metadata (duration, resolution, codec, etc.) for a media file.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/media/metadata",
        headers=_get_headers(),
        json={"media_url": media_url}
    )
    return response.json()


# ============================================================
# CLOUD STORAGE FUNCTIONS
# ============================================================

@func.register_function(
    metadata={"description": "Upload file to S3-compatible storage."},
    key_dependencies=["nca_api_key", "s3_access_key", "s3_secret_key"],
    input_parameters=[
        {"name": "file_url", "type": "str", "description": "URL of file to upload"},
        {"name": "bucket", "type": "str", "description": "S3 bucket name"},
        {"name": "key", "type": "str", "description": "Object key/path in bucket"}
    ]
)
def nca_upload_to_s3(
    file_url: str, 
    bucket: str, 
    key: str
) -> Dict[str, Any]:
    """
    Upload a file to S3-compatible storage.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/s3/upload",
        headers=_get_headers(),
        json={
            "file_url": file_url,
            "bucket": bucket,
            "key": key
        }
    )
    return response.json()


@func.register_function(
    metadata={"description": "Upload file to Google Cloud Storage."},
    key_dependencies=["nca_api_key", "gcp_credentials"],
    input_parameters=[
        {"name": "file_url", "type": "str", "description": "URL of file to upload"},
        {"name": "bucket", "type": "str", "description": "GCS bucket name"},
        {"name": "key", "type": "str", "description": "Object key/path in bucket"}
    ]
)
def nca_upload_to_gcs(
    file_url: str, 
    bucket: str, 
    key: str
) -> Dict[str, Any]:
    """
    Upload a file to Google Cloud Storage.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/gcp/upload",
        headers=_get_headers(),
        json={
            "file_url": file_url,
            "bucket": bucket,
            "key": key
        }
    )
    return response.json()


# ============================================================
# PYTHON EXECUTION
# ============================================================

@func.register_function(
    metadata={"description": "Execute Python code remotely in a sandboxed environment."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "code", "type": "str", "description": "Python code to execute"},
        {"name": "timeout", "type": "int", "description": "Execution timeout in seconds"}
    ]
)
def nca_execute_python(
    code: str, 
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Execute Python code in a sandboxed environment.
    Useful for data processing, calculations, etc.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/code/execute/python",
        headers=_get_headers(),
        json={
            "code": code,
            "timeout": timeout
        }
    )
    return response.json()


# ============================================================
# JOB STATUS
# ============================================================

@func.register_function(
    metadata={"description": "Check the status of an async job."},
    key_dependencies=["nca_api_key"],
    input_parameters=[
        {"name": "job_id", "type": "str", "description": "Job ID to check"}
    ]
)
def nca_get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Check the status of an async job.
    """
    response = requests.post(
        f"{NCA_BASE_URL}/v1/toolkit/job/status",
        headers=_get_headers(),
        json={"job_id": job_id}
    )
    return response.json()


# ============================================================
# HEALTH CHECK
# ============================================================

@func.register_function(
    metadata={"description": "Check if NCA Toolkit API is running and healthy."}
)
def nca_health_check() -> Dict[str, Any]:
    """
    Check the health status of the NCA Toolkit API.
    """
    try:
        response = requests.get(
            f"{NCA_BASE_URL}/v1/toolkit/test",
            headers=_get_headers(),
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}
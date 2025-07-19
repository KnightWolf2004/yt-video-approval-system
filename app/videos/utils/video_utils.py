import os
from app.videos.models.video_model import Video


MAX_FILE_SIZE = 1024 * 1024 * 1024 * 4
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..', 'uploads'))

ALLOWED_VIDEO_MIME_TYPES = [
    "video/mp4",
    "video/x-matroska",
    "video/webm",
    "video/x-msvideo",
    "video/quicktime",
    "video/x-flv",
    "video/mpeg",
    "video/ogg",
    "video/3gpp",
    "video/x-ms-wmv",
    "video/x-m4v",
    ]

def get_extra_fields(video: Video):
    return {"uploader": video.uploader.name, "reviewer": video.reviewer.name}

class MaxBodySizeException(Exception):
    def __init__(self, body_len: int):
        self.body_len = body_len

class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)
        
async def check_for_allowed_types(mime_type: str):
    if mime_type in ALLOWED_VIDEO_MIME_TYPES:
        return True
    else:
        return False
    
async def remove_partial_file(filepath: str):
    if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
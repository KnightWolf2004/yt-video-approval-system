import os

from fastapi import HTTPException, status
import jwt
from jwt.exceptions import PyJWTError
from app.videos.models.video_model import Video


MAX_FILE_SIZE = 1024 * 1024 * 1024 * 4
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..', 'uploads'))
CHUNK_SIZE = 1024 * 1024

ALLOWED_VIDEO_MIME_TYPES = [
    "video/mp4",
    # "video/x-matroska",
    # "video/webm",
    # "video/x-msvideo",
    # "video/quicktime",
    # "video/x-flv",
    # "video/mpeg",
    # "video/ogg",
    # "video/3gpp",
    # "video/x-ms-wmv",
    # "video/x-m4v",
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

async def get_range(range_header: str|None, file_size: int):
    if range_header is None:
        return 0, file_size -1
    units, _, range_spec = range_header.partition("=")
    if units != "bytes":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid unit in range header")
    start_str, end_str = range_spec.split("-")
    start = int(start_str) if start_str else 0
    end = int(end_str) if end_str else min(start + CHUNK_SIZE - 1, file_size - 1)
    if start > end or end >= file_size:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, detail="Requested Range not satisfiable")
    return start, end

def iterfile(path, start: int, end: int):
    with open(path, "rb") as video:
        video.seek(start)
        bytes_to_read = end - start + 1
        while bytes_to_read > 0:
            chunk_size = min(CHUNK_SIZE, bytes_to_read)
            data = video.read(chunk_size)
            if not data:
                break
            yield data
            bytes_to_read -= len(data)

def check_url(token: str):
    SECRET_KEY = os.getenv("SECRET_KEY")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        video_id = payload["video_id"]
    except PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    return video_id
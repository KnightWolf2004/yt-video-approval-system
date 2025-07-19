import os
from app.videos.models.video_model import Video


MAX_FILE_SIZE = 1024 * 1024 * 1024 * 4
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..', 'uploads'))


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
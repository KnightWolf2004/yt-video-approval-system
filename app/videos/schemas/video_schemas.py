from pydantic import field_serializer
from sqlmodel import SQLModel

from app.videos.models.video_enums import Status


class VideoCreate(SQLModel):
    filename: str
    url: str

class VideoResponse(SQLModel):
    id: int
    filename: str
    url: str
    status: Status
    uploader: str
    reviewer: str

    @field_serializer('status')
    def serialize_status(self, status: Status):
        return status.name

class VideoDelete(SQLModel):
    id: int

class VideoUpdateStatus(SQLModel):
    id: int
    status: Status

class VideoStream(SQLModel):
    id: int
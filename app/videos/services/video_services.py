import os
from fastapi import HTTPException, Request, status
from sqlmodel import Session
import streaming_form_data
from urllib.parse import unquote
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from streaming_form_data.validators import MaxSizeValidator
from starlette.requests import ClientDisconnect
import streaming_form_data.validators

from app.users.models.user_enums import Role
from app.users.models.user_model import User
from app.videos.models.video_model import Video
from app.videos.schemas.video_schemas import VideoCreate, VideoDelete, VideoUpdateStatus
from app.videos.utils.video_utils import MAX_FILE_SIZE, MAX_REQUEST_BODY_SIZE, UPLOAD_DIR, MaxBodySizeException, MaxBodySizeValidator


def handle_videos_read(session: Session, user: User):
    if user.role == Role.Admin:
        videos = user.reviewed
    elif user.role == Role.Editor: 
        videos = user.uploaded
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No role assigned to user")
    
    return videos
    
def handle_video_update(session: Session, video: VideoUpdateStatus, user: User):
    db_video = session.get(Video, video.id)
    if db_video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    if db_video.reviewed_by != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    update = {"status": video.status}
    db_video.sqlmodel_update(update)
    session.add(db_video)
    session.commit()
    session.refresh(db_video)
    return db_video

def handle_video_delete(session: Session, video: VideoDelete, user: User):
    db_video = session.get(Video, video.id)
    if db_video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    if db_video.uploaded_by != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    session.delete(db_video)
    session.commit()
    return {"message": "Video deleted successfully"}

async def handle_video_upload(request: Request, user: User, session: Session):
    uploaded_by = user.id
    reviewed_by = user.admin_id

    reviewer = session.get(User, reviewed_by)
    if reviewer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Admin found")

    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)
    filename = request.headers.get('filename')

    if not filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Filename header is missing')
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = unquote(filename)
        filepath = os.path.join(UPLOAD_DIR, os.path.basename(filename))
        file_ = FileTarget(filepath, validator=MaxSizeValidator(MAX_FILE_SIZE))
        data = ValueTarget()
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register('file', file_)
        parser.register('data', data)

        async for chunk in request.stream():
            body_validator(chunk)
            parser.data_received(chunk)
    except ClientDisconnect:
        print("Client Disconnected")
    except MaxBodySizeException as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f'Maximum request body size limit ({MAX_REQUEST_BODY_SIZE} bytes) exceeded ({e.body_len} bytes read)')
    except streaming_form_data.validators.ValidationError:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f'Maximum file size limit ({MAX_FILE_SIZE} bytes) exceeded')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='There was an error uploading the file')
    
    if not file_.multipart_filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='File is missing')
    
    print(data.value.decode())
    print(file_.multipart_filename)

    extra_data = {"uploaded_by": uploaded_by, "reviewed_by": reviewed_by, "filename": filename, "url": filepath}
    video = Video(**extra_data)
    video.uploader = user
    video.reviewer = reviewer
    session.add(video)
    session.commit()

    return {"message": f"Successfully uploaded {filename}"}
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.main import get_session
from app.utils.shared_utils import serialize_list
from app.videos.schemas.video_schemas import VideoCreate, VideoDelete, VideoResponse, VideoUpdateStatus
from app.videos.services.video_services import handle_video_delete, handle_video_update, handle_video_upload, handle_videos_read


router = APIRouter(prefix='/videos', tags=['Video'])

@router.post('/upload', response_model=VideoResponse)                               #TODO: Add @employee_required dependency
def upload_video(*, session: Session = Depends(get_session), video: VideoCreate):
    video_db = handle_video_upload(session, video)
    return VideoResponse.model_validate(video_db)

@router.get('/my-videos', response_model=list[VideoResponse])
def read_uploads(*, session: Session = Depends(get_session)):
    videos_db = handle_videos_read(session)
    return serialize_list(videos_db, VideoResponse)

@router.patch('/review', response_model=VideoResponse)                                  #TODO: Add @admin_required dependency
def update_status(*, session: Session = Depends(get_session), video: VideoUpdateStatus):
    video_db = handle_video_update(session, video)
    return VideoResponse.model_validate(video_db)

@router.delete('/delete')                                                               #TODO: Add @employee_required dependency
def delete_video(*, session: Session = Depends(get_session), video: VideoDelete):
    return handle_video_delete(session, video)
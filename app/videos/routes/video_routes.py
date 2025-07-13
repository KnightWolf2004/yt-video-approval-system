from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.session import get_session
from app.users.models.user_model import User
from app.utils.shared_utils import serialize_list
from app.videos.schemas.video_schemas import VideoCreate, VideoDelete, VideoResponse, VideoUpdateStatus
from app.videos.services.video_services import handle_video_delete, handle_video_update, handle_video_upload, handle_videos_read
from app.auth.dependencies.auth_dependencies import admin_required, editor_required
from app.auth.services.auth_services import get_current_active_user

router = APIRouter(prefix='/videos', tags=['Video'])

@router.post('/upload', response_model=VideoResponse)
def upload_video(*, current_user: User = Depends(editor_required), session: Session = Depends(get_session), video: VideoCreate):
    video_db = handle_video_upload(session=session, video=video, uploader=current_user)
    return VideoResponse.model_validate(video_db)

@router.get('/my-videos', response_model=list[VideoResponse])
def read_uploads(*, current_user: User = Depends(get_current_active_user), session: Session = Depends(get_session)):
    videos_db = handle_videos_read(session=session, user=current_user)
    return serialize_list(videos_db, VideoResponse)

@router.patch('/review', response_model=VideoResponse)
def update_status(*, current_user: User = Depends(admin_required), session: Session = Depends(get_session), video: VideoUpdateStatus):
    video_db = handle_video_update(session=session, video=video, user=current_user)
    return VideoResponse.model_validate(video_db)

@router.delete('/delete')
def delete_video(*, current_user: User = Depends(editor_required), session: Session = Depends(get_session), video: VideoDelete):
    return handle_video_delete(session=session, video=video, user=current_user)
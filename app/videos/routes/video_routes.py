import os
from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from fastapi.templating import Jinja2Templates

from app.core.session import get_session
from app.users.models.user_model import User
from app.utils.shared_utils import serialize_list
from app.videos.schemas.video_schemas import VideoDelete, VideoResponse, VideoUpdateStatus
from app.videos.services.video_services import handle_signed_url_generate, handle_video_delete, handle_video_stream, handle_video_update, handle_video_upload, handle_videos_read
from app.auth.dependencies.auth_dependencies import admin_required, editor_required
from app.auth.services.auth_services import get_current_active_user
from app.videos.utils.video_utils import check_url, get_extra_fields

router = APIRouter(prefix='/videos', tags=['Video'])


templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent/"templates"))

@router.get('/my-videos', response_model=list[VideoResponse])
def read_uploads(*, current_user: User = Depends(get_current_active_user), session: Session = Depends(get_session)):
    videos_db = handle_videos_read(session=session, user=current_user)

    return serialize_list(videos_db, VideoResponse, extra_fields_func=get_extra_fields)

@router.patch('/review', response_model=VideoResponse)
def update_status(*, current_user: User = Depends(admin_required), session: Session = Depends(get_session), video: VideoUpdateStatus):
    video_db = handle_video_update(session=session, video=video, user=current_user)
    extra_field = {"uploader": video_db.uploader.name, "reviewer": video_db.reviewer.name}
    return VideoResponse.model_validate(video_db, update=extra_field)

@router.delete('/delete')
def delete_video(*, current_user: User = Depends(editor_required), session: Session = Depends(get_session), video: VideoDelete):
    return handle_video_delete(session=session, video=video, user=current_user)

@router.post('/upload')
async def upload(request: Request, user: User = Depends(editor_required), session: Session = Depends(get_session)):
    return await handle_video_upload(request, user, session)

@router.get("/generate-stream-url")
async def generate_signed_stream_url(video_id: int, user: User = Depends(get_current_active_user), session: Session = Depends(get_session)):
    return await handle_signed_url_generate(video_id, user, session)

@router.get("/stream-signed")
async def stream_video_signed(token: str, request: Request, session: Session = Depends(get_session)):
    video_id = check_url(token)
    return await handle_video_stream(video_id=video_id, request=request, session=session)

@router.get("/watch", response_class=HTMLResponse)
async def watch_video_page(request: Request):
    return templates.TemplateResponse("stream.html", {"request": request})
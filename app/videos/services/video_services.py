from fastapi import HTTPException, status
from sqlmodel import Session

from app.users.models.user_enums import Role
from app.users.models.user_model import User
from app.videos.models.video_model import Video
from app.videos.schemas.video_schemas import VideoCreate, VideoDelete, VideoUpdateStatus


def handle_video_upload(session: Session, video: VideoCreate, uploader: User):
    uploaded_by = uploader.id
    reviewed_by = uploader.admin_id

    extra_data = {"uploaded_by": uploaded_by, "reviewed_by": reviewed_by}
    db_video = Video.model_validate(video, update=extra_data)

    db_video.uploader = uploader

    reviewer = session.get(User, reviewed_by)
    if reviewer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Admin found")
    db_video.reviewer = reviewer

    session.add(db_video)
    session.commit()
    session.refresh(db_video)
    return db_video

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
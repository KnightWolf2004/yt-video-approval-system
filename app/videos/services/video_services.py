from fastapi import HTTPException, status
from sqlmodel import Session

from app.users.models.user_enums import Role
from app.users.models.user_model import User
from app.videos.models.video_model import Video
from app.videos.schemas.video_schemas import VideoCreate, VideoDelete, VideoUpdateStatus


def handle_video_upload(session: Session, video: VideoCreate):
    uploaded_by = 0  # TODO: Get from token
    reviewed_by = 0  # TODO: Get from token

    extra_data = {"uploaded_by": uploaded_by, "reviewed_by": reviewed_by}
    db_video = Video.model_validate(video, update=extra_data)

    uploader = session.get(User, uploaded_by)
    if uploader is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not valid account")
    db_video.uploader = uploader

    reviewer = session.get(User, reviewed_by)
    if reviewer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Admin found")
    db_video.reviewer = reviewer

    session.add(db_video)
    session.commit()
    session.refresh(db_video)

    return db_video

def handle_videos_read(session: Session):
    db_user = session.get(User, 0)                                                 #TODO: get user id
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if db_user.role == Role.Admin:
        videos = db_user.reviewed
    elif db_user.role == Role.Editor: 
        videos = db_user.uploaded
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No role assigned to user")
    
    if not videos:
        return []
    else:
        return videos
    
def handle_video_update(session: Session, video: VideoUpdateStatus):
    db_video = session.get(Video, video.id)
    if db_video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    user = session.get(User, 0)                                                         #TODO: get user id
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if db_video.reviewed_by != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    update = {"status": video.status}
    db_video.sqlmodel_update(update)
    session.add(db_video)
    session.commit()
    session.refresh(db_video)
    return db_video

def handle_video_delete(session: Session, video: VideoDelete):
    db_video = session.get(Video, video.id)
    if db_video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    user = session.get(User, 0)                                                         #TODO: get user id
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="In valid user")
    if db_video.uploaded_by != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    session.delete(db_video)
    session.commit()
    return {"message": "Video deleted successfully"}
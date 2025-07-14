from app.videos.models.video_model import Video


def get_extra_fields(video: Video):
    return {"uploader": video.uploader.name, "reviewer": video.reviewer.name}
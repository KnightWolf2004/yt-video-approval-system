from sqlalchemy import Column, Text
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum as SQLEnum
from typing import TYPE_CHECKING
from sqlalchemy.orm import declared_attr
from app.videos.models.video_enums import Status
from app.users.models.user_model import User


if TYPE_CHECKING:
    from app.users.models.user_model import User

class Video(SQLModel, table=True):
    @declared_attr #type: ignore
    def __tablename__(cls) -> str:
        return "videos"
    
    id: int | None = Field(default=None, primary_key=True)
    filename: str
    url: str = Field(sa_column=Column(Text))
    status: Status | None = Field(sa_column=Column(SQLEnum(Status)), default=Status.Working)
    uploaded_by: int = Field(foreign_key="users.id")
    reviewed_by: int = Field(foreign_key="users.id")

    uploader: User = Relationship(back_populates="uploaded", sa_relationship_kwargs={"foreign_keys": "[Video.uploaded_by]"})
    reviewer: User = Relationship(back_populates="reviewed", sa_relationship_kwargs={"foreign_keys": "[Video.reviewed_by]"})
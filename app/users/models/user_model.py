from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import declared_attr

from app.users.models.user_enums import Role


if TYPE_CHECKING:
    from app.videos.models.video_model import Video

class User(SQLModel, table=True):
    @declared_attr #type: ignore
    def __tablename__(cls) -> str:
        return "users"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str
    username: str = Field(index=True, unique=True)
    password: str
    role: Role = Field(sa_column=Column(SQLEnum(Role)))
    admin_id: int | None = Field(default=None, foreign_key="users.id")

    editors: list["User"] = Relationship(back_populates="admin", cascade_delete=True)
    admin: Optional["User"] = Relationship(back_populates="editors", sa_relationship_kwargs={"remote_side": "User.id"})
    uploaded: list["Video"] = Relationship(back_populates="uploader", sa_relationship_kwargs={"foreign_keys": "[Video.uploaded_by]"})
    reviewed: list["Video"] = Relationship(back_populates="reviewer", sa_relationship_kwargs={"foreign_keys": "[Video.reviewed_by]"})
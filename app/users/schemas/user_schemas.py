from sqlmodel import SQLModel

from app.users.models.user_enums import Role


class UserCreate(SQLModel):
    name: str
    username: str
    password: str

class UserResponse(SQLModel):
    name: str
    username: str
    role: Role

class EditorDelete(SQLModel):
    id: int | None = None
    username: str
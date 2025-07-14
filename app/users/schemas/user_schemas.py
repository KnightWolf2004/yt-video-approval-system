from pydantic import field_serializer
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

    @field_serializer('role')
    def serialize_role(self, role: Role):
        return role.name

class EditorDelete(SQLModel):
    id: int | None = None
    username: str
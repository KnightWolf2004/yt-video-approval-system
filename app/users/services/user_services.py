from fastapi import HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.auth.utils.auth_utils import get_password_hash
from app.users.models.user_enums import Role
from app.users.models.user_model import User
from app.users.schemas.user_schemas import EditorDelete, UserCreate


def handle_user_create(session: Session, user: UserCreate):
    password = get_password_hash(user.password)                                           
    extra_data = {"password": password, "role": Role.Admin}
    user_db = User.model_validate(user, update=extra_data)
    session.add(user_db)
    try:
        session.commit()
        session.refresh(user_db)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    return user_db
    
def handle_editor_create(session: Session, user: UserCreate, admin: User):
    admin_id = admin.id
    extra_data = {"role": Role.Editor, "admin_id": admin_id}
    db_user = User.model_validate(user, update=extra_data)
    db_user.admin = admin
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def handle_editor_read(session: Session, admin: User):
    editor = admin.editors
    if not editor:
        return []
    else:
        return editor
    
def handle_user_delete(session: Session, user: User):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    session.delete(user)
    session.commit()
    return {"Your account has been deleted"}

def handle_editor_delete(session: Session, editor: EditorDelete, user: User):
    db_editor = session.get(User, editor.id)
    if db_editor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such editor")
    if user.id != db_editor.admin_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such editor")
    
    session.delete(db_editor)
    session.commit()
    return {"Your editor has been deleted"}
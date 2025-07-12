from fastapi import HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.auth.utils.auth_utils import get_password_hash
from app.users.models.user_enums import Role
from app.users.models.user_model import User
from app.users.schemas.user_schemas import EditorDelete, UserCreate


def handle_user_read(session: Session):
    user = session.get(User,0)                                                          #TODO: get user id somehow.
    return user

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
    
def handle_editor_create(session: Session, user: UserCreate):
    extra_data = {"role": Role.Editor, "admin_id": 0}                                #TODO: get admin id somehow.
    db_user = User.model_validate(user, update=extra_data)
    db_user_admin = session.get(User,0)                                                #TODO: get admin id somehow.
    db_user.admin = db_user_admin
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def handle_editor_read(session: Session):
    user = session.get(User, 0)                                                         #TODO: get user id somehow.
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")#401
    editor = user.editors
    if not editor:
        return []
    else:
        return editor
    
def handle_user_delete(session: Session):
    user = session.get(User, 0)                                                          #TODO: get user id somehow.
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    session.delete(user)
    session.commit()
    return {"Your account has been deleted"}

def handle_editor_delete(session: Session, user: EditorDelete):
    admin = session.get(User, 0)                                                          #TODO: get user id somehow.
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
    db_user = session.get(User, user.id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such editor")
    if admin.id != db_user.admin_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such editor")
    
    session.delete(db_user)
    session.commit()
    return {"Your editor has been deleted"}
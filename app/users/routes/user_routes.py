from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.main import get_session
from app.users.models.user_model import User
from app.users.schemas.user_schemas import EditorDelete, UserCreate, UserResponse
from app.users.services.user_services import handle_editor_create, handle_editor_delete, handle_editor_read, handle_user_create, handle_user_delete
from app.utils.shared_utils import serialize_list
from app.auth.services.auth_services import get_current_active_user
from app.auth.dependencies.auth_dependencies import admin_required, editor_required


router = APIRouter(prefix='/user', tags=['User'])

@router.post('/register/admin', response_model=UserResponse)
def register_admin(*, session: Session = Depends(get_session), user: UserCreate):
    user_db = handle_user_create(session, user)
    return UserResponse.model_validate(user_db)

@router.post('/register/editor', response_model=UserResponse)                        #TODO: Add @admin_required dependency
def register_employee(*, admin: User = Depends(admin_required), session: Session = Depends(get_session), user: UserCreate):
    editor = handle_editor_create(session, user, admin)
    return UserResponse.model_validate(editor)

@router.get("/", response_model=UserResponse)
def read_user(*, current_user: User = Depends(get_current_active_user)):
    return UserResponse.model_validate(current_user)

@router.get('/editors', response_model=list[UserResponse])
def read_all_editors(*, admin: User = Depends(admin_required), session: Session = Depends(get_session)):
    editors =  handle_editor_read(session=session, admin=admin)
    return serialize_list(editors, UserResponse)

@router.delete('/me')
def delete_admin(*, current_user: User = Depends(get_current_active_user), session: Session = Depends(get_session)):
    return handle_user_delete(session=session, user=current_user)

@router.delete('/delete/editor')
def delete_editor(*,current_user: User = Depends(get_current_active_user) ,session: Session = Depends(get_session), editor: EditorDelete):
    return handle_editor_delete(session=session, editor=editor, user=current_user)
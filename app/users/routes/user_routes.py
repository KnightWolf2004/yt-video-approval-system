from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.main import get_session
from app.users.schemas.user_schemas import EditorDelete, UserCreate, UserResponse
from app.users.services.user_services import handle_editor_create, handle_editor_delete, handle_editor_read, handle_user_create, handle_user_delete, handle_user_read
from app.utils.shared_utils import serialize_list


router = APIRouter(prefix='/user', tags=['User'])

@router.post('/register/admin', response_model=UserResponse)
def register_admin(*, session: Session = Depends(get_session), user: UserCreate):
    user_db = handle_user_create(session, user)
    return UserResponse.model_validate(user_db)

@router.post('/register/editor', response_model=UserResponse)                        #TODO: Add @admin_required dependency
def register_employee(*, session: Session = Depends(get_session), user: UserCreate):
    editor = handle_editor_create(session, user)
    return UserResponse.model_validate(editor)

@router.get("/", response_model=UserResponse)
def read_user(*, session: Session = Depends(get_session)):
    user =  handle_user_read(session)
    return UserResponse.model_validate(user)

@router.get('/editors', response_model=list[UserResponse])                            #TODO: Add @admin_required dependency
def read_all_editors(*, session: Session = Depends(get_session)):
    editors =  handle_editor_read(session)
    return serialize_list(editors, UserResponse)

@router.delete('/admin')                                                                #TODO: Add @admin_required dependency
def delete_admin(*, session: Session = Depends(get_session)):
    return handle_user_delete(session)

@router.delete('/editor')                                                        #TODO: Add @admin_required dependency
def delete_editor(*, session: Session = Depends(get_session), user: EditorDelete):
    return handle_editor_delete(session, user)
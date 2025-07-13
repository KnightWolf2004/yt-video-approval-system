from fastapi import Depends, HTTPException, status

from app.auth.services.auth_services import get_current_active_user
from app.users.models.user_enums import Role
from app.users.models.user_model import User


def admin_required(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != Role.Admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only",
        )
    return current_user

def editor_required(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != Role.Editor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor only",
        )
    return current_user
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
import os
from datetime import timedelta, datetime, timezone
from jwt.exceptions import InvalidTokenError

from app.auth.schemas.token import TokenData
from app.auth.utils.auth_utils import verify_password
from app.core.session import get_session
from app.users.models.user_model import User
from app.users.utils.user_utils import get_user_by_username


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def authenticate_user(username: str, password: str, session: Session = Depends(get_session)):
    # user_statement = select(User).where(User.username == username)
    # user = session.exec(user_statement).first()
    user =  get_user_by_username(session, username)
    if user is None:
        return False
    if not verify_password(password, user.password):
        return False
    return user
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    extra_data = {"exp": expire}
    to_encode.update(extra_data)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    statement = select(User).where(User.username==token_data.username)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user))->User:
    return current_user
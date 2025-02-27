import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from pydantic import ValidationError
from app.core.config import settings
from app.db.database import get_db
from app.models.model_user import User
from sqlalchemy.orm import Session
from starlette import status

from app.repositories.user_role_repository import (
    UserRoleRepository,
    get_user_role_repository,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
reusable_oauth2 = HTTPBearer(scheme_name="Authorization")


def verify_password(password, hash_password):
    return pwd_context.verify(password, hash_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.SECURITY_ALGORITHM
    )


def get_current_user(
    http_authorization_credentials: str = Depends(reusable_oauth2),
    session: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            http_authorization_credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.SECURITY_ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Không thể xác thực thông tin đăng nhập"
            )
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token không hợp lệ"
        )
    user = session.query(User).filter(User.user_name == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không thể xác thực thông tin đăng nhập 3",
        )
    return user


def check_permissions(required_roles: list[str]):
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        user_role_repository: UserRoleRepository = Depends(get_user_role_repository),
    ):
        user_roles = user_role_repository.get_role_names_by_user_id(current_user.id)
        if not any(role in required_roles for role in user_roles):
            raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập")
        return current_user

    return permission_checker

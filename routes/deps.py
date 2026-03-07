import sqlite3

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from data.base import get_db
from repositories.admin_repo import AdminRepo
from services.auth_service import AuthService
from services.exceptions import AuthError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: sqlite3.Connection = Depends(get_db),
):
    auth_service = AuthService(AdminRepo(db))
    try:
        return auth_service.current_admin_from_token(token)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_privilege(privilege: str):
    def _checker(current_admin=Depends(get_current_admin)):
        privileges = current_admin.get("privileges", [])
        if privilege not in privileges and "super_admin" not in privileges:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required privilege: {privilege}",
            )
        return current_admin

    return _checker

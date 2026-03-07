import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from data.base import get_db
from IO.admin import AdminCreate, AdminOut, TokenOut
from repositories.admin_repo import AdminRepo
from services.auth_service import AuthService
from services.exceptions import AuthError, ValidationError

router = APIRouter(prefix="/auth", tags=["auth"])


def _service(db: sqlite3.Connection) -> AuthService:
    return AuthService(AdminRepo(db))


@router.post("/bootstrap-admin", response_model=AdminOut, status_code=201)
def bootstrap_admin(payload: AdminCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        return _service(db).bootstrap_admin(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/token", response_model=TokenOut)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: sqlite3.Connection = Depends(get_db),
):
    try:
        return _service(db).login(form_data.username, form_data.password)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

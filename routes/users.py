import sqlite3
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from data.base import get_db
from IO.user import UserCreate, UserOut, UserUpdate
from repositories.user_repo import UserRepository
from services.exceptions import ConflictError, NotFoundError, ValidationError
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def _service(db: sqlite3.Connection) -> UserService:
    return UserService(UserRepository(db))


@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    service = _service(db)
    try:
        return service.create_user(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=List[UserOut])
def list_users(
    q: Optional[str] = Query(None, description="Filter by username or email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
):
    return _service(db).list_users(q=q, limit=limit, offset=offset)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        return _service(db).get_user(user_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: sqlite3.Connection = Depends(get_db),
):
    service = _service(db)
    try:
        return service.update_user(user_id, payload)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{user_id}")
def delete_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        return _service(db).delete_user(user_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

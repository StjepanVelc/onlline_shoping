import sqlite3
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from data.base import get_db
from IO.admin import AdminCreate, AdminOut, AdminUpdate
from repositories.admin_repo import AdminRepo
from routes.deps import get_current_admin, require_privilege
from services.admin_service import AdminService
from services.exceptions import ConflictError, NotFoundError, ValidationError

router = APIRouter(prefix="/admins", tags=["admins"])


def _service(db: sqlite3.Connection) -> AdminService:
    return AdminService(AdminRepo(db))


require_manage_admins = require_privilege("manage_admins")


@router.post("", response_model=AdminOut, status_code=201)
def create_admin(
    payload: AdminCreate,
    db: sqlite3.Connection = Depends(get_db),
    _admin=Depends(require_manage_admins),
):
    try:
        return _service(db).create_admin(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=List[AdminOut])
def list_admins(
    q: Optional[str] = Query(None, description="Filter by username or email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    return _service(db).list_admins(q=q, limit=limit, offset=offset)


@router.get("/{admin_id}", response_model=AdminOut)
def get_admin(
    admin_id: int,
    db: sqlite3.Connection = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    try:
        return _service(db).get_admin(admin_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{admin_id}", response_model=AdminOut)
def update_admin(
    admin_id: int,
    payload: AdminUpdate,
    db: sqlite3.Connection = Depends(get_db),
    _admin=Depends(require_manage_admins),
):
    service = _service(db)
    try:
        return service.update_admin(admin_id, payload)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{admin_id}")
def delete_admin(
    admin_id: int,
    db: sqlite3.Connection = Depends(get_db),
    _admin=Depends(require_manage_admins),
):
    try:
        return _service(db).delete_admin(admin_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

import sqlite3
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from data.base import get_db
from IO.product import OrderCreate, OrderDetailOut, OrderOut, OrderSummaryOut
from repositories.order_repo import OrderRepository
from repositories.product_repo import ProductRepository
from repositories.user_repo import UserRepository
from services.exceptions import NotFoundError, ValidationError
from services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


def _service(db: sqlite3.Connection) -> OrderService:
    return OrderService(
        order_repo=OrderRepository(db, autocommit=False),
        user_repo=UserRepository(db, autocommit=False),
        product_repo=ProductRepository(db, autocommit=False),
        db=db,
    )


@router.post("", response_model=OrderOut, status_code=201)
def create_order(payload: OrderCreate, db: sqlite3.Connection = Depends(get_db)):
    service = _service(db)
    try:
        return service.create_order(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=List[OrderSummaryOut])
def list_orders(
    user_id: Optional[int] = Query(None, ge=1),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
):
    return _service(db).list_orders(
        user_id=user_id,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get("/{order_id}", response_model=OrderDetailOut)
def get_order(order_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        return _service(db).get_order_details(order_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

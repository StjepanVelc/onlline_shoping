import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from data.base import get_db
from IO.product import OrderCreate, OrderOut
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

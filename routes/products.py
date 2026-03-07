import sqlite3
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from data.base import get_db
from IO.product import ProductCreate, ProductOut, ProductUpdate
from repositories.product_repo import ProductRepository
from services.exceptions import NotFoundError, ValidationError
from services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


def _service(db: sqlite3.Connection) -> ProductService:
    return ProductService(ProductRepository(db))


@router.post("", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: sqlite3.Connection = Depends(get_db)):
    return _service(db).create_product(payload)


@router.get("", response_model=List[ProductOut])
def list_products(
    q: Optional[str] = Query(None, description="Filter by product name/description"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
):
    return _service(db).list_products(q=q, limit=limit, offset=offset)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        return _service(db).get_product(product_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: sqlite3.Connection = Depends(get_db),
):
    service = _service(db)
    try:
        return service.update_product(product_id, payload)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{product_id}")
def delete_product(product_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        return _service(db).delete_product(product_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

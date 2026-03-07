import sqlite3
import json
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response

from data.base import get_db, lifespan
from IO.admin import AdminCreate, AdminOut, AdminUpdate
from IO.product import (
    OrderCreate,
    OrderOut,
    ProductCreate,
    ProductOut,
    ProductUpdate,
)
from IO.user import UserCreate, UserOut, UserUpdate

app = FastAPI(title="Shop API (SQLite)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.post("/users", response_model=UserOut, tags=["users"], status_code=201)
def create_user(payload: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users (username, email, country) VALUES (?, ?, ?)",
            (payload.username, payload.email, payload.country),
        )
        user_id = cur.lastrowid
        db.commit()
        row = db.execute(
            "SELECT id, username, email, country FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return UserOut(**dict(row))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Username or email already exists"
        ) from exc


@app.get("/users", response_model=List[UserOut], tags=["users"])
def list_users(
    q: Optional[str] = Query(None, description="Filter by username or email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
):
    sql = "SELECT id, username, email, country FROM users"
    params: List[object] = []
    if q:
        sql += " WHERE username LIKE ? OR email LIKE ?"
        like = f"%{q}%"
        params.extend([like, like])
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = db.execute(sql, params).fetchall()
    return [UserOut(**dict(row)) for row in rows]


@app.get("/users/{user_id}", response_model=UserOut, tags=["users"])
def get_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute(
        "SELECT id, username, email, country FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(**dict(row))


@app.patch("/users/{user_id}", response_model=UserOut, tags=["users"])
def update_user(
    user_id: int, payload: UserUpdate, db: sqlite3.Connection = Depends(get_db)
):
    fields, params = [], []
    for col in ("username", "email", "country"):
        val = getattr(payload, col)
        if val is not None:
            fields.append(f"{col} = ?")
            params.append(val)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(user_id)
    try:
        cur = db.cursor()
        cur.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", params)
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        db.commit()
        row = db.execute(
            "SELECT id, username, email, country FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return UserOut(**dict(row))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Username or email already exists"
        ) from exc


@app.delete("/users/{user_id}", tags=["users"])
def delete_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True, "id": user_id}


@app.post("/products", response_model=ProductOut, tags=["products"], status_code=201)
def create_product(payload: ProductCreate, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
        (payload.name, payload.description, payload.price, payload.stock),
    )
    db.commit()
    product_id = cur.lastrowid
    row = db.execute(
        "SELECT id, name, description, price, stock FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    return ProductOut(**dict(row))


@app.get("/products", response_model=List[ProductOut], tags=["products"])
def list_products(
    q: Optional[str] = Query(None, description="Filter by product name/description"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
):
    sql = "SELECT id, name, description, price, stock FROM products"
    params: List[object] = []
    if q:
        sql += " WHERE name LIKE ? OR description LIKE ?"
        like = f"%{q}%"
        params.extend([like, like])
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = db.execute(sql, params).fetchall()
    return [ProductOut(**dict(row)) for row in rows]


@app.get("/products/{product_id}", response_model=ProductOut, tags=["products"])
def get_product(product_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute(
        "SELECT id, name, description, price, stock FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut(**dict(row))


@app.patch("/products/{product_id}", response_model=ProductOut, tags=["products"])
def update_product(
    product_id: int, payload: ProductUpdate, db: sqlite3.Connection = Depends(get_db)
):
    fields, params = [], []
    for col in ("name", "description", "price", "stock"):
        val = getattr(payload, col)
        if val is not None:
            fields.append(f"{col} = ?")
            params.append(val)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(product_id)
    cur = db.cursor()
    cur.execute(f"UPDATE products SET {', '.join(fields)} WHERE id = ?", params)
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    db.commit()
    return get_product(product_id, db)


@app.delete("/products/{product_id}", tags=["products"])
def delete_product(product_id: int, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": True, "id": product_id}


@app.post("/orders", response_model=OrderOut, tags=["orders"], status_code=201)
def create_order(payload: OrderCreate, db: sqlite3.Connection = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    try:
        db.execute("BEGIN")
        cur = db.cursor()
        cur.execute(
            "INSERT INTO orders (user_id, address, status) VALUES (?, ?, 'pending')",
            (payload.user_id, payload.address),
        )
        order_id = cur.lastrowid

        total = 0.0
        for item in payload.items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (order_id, item.product_id, item.quantity, item.price),
            )
            total += item.quantity * item.price

        cur.execute("UPDATE orders SET total_amount = ? WHERE id = ?", (total, order_id))
        db.commit()

        row = db.execute(
            "SELECT id, user_id, address, status, total_amount FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()
        return OrderOut(**dict(row))
    except sqlite3.IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid user_id or product_id reference in order payload",
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Order failed: {exc}") from exc


# ========== ADMINS CRUD ==========


@app.post("/admins", response_model=AdminOut, tags=["admins"], status_code=201)
def create_admin(payload: AdminCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.cursor()
        privileges_json = json.dumps(payload.privileges)
        cur.execute(
            "INSERT INTO admins (username, email, privileges) VALUES (?, ?, ?)",
            (payload.username, payload.email, privileges_json),
        )
        admin_id = cur.lastrowid
        db.commit()
        row = db.execute(
            "SELECT id, username, email, privileges FROM admins WHERE id = ?",
            (admin_id,),
        ).fetchone()
        return AdminOut(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            privileges=json.loads(row["privileges"]),
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Username or email already exists"
        ) from exc


@app.get("/admins", response_model=List[AdminOut], tags=["admins"])
def list_admins(
    q: Optional[str] = Query(None, description="Filter by username or email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: sqlite3.Connection = Depends(get_db),
):
    sql = "SELECT id, username, email, privileges FROM admins"
    params: List[object] = []
    if q:
        sql += " WHERE username LIKE ? OR email LIKE ?"
        like = f"%{q}%"
        params.extend([like, like])
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = db.execute(sql, params).fetchall()
    return [
        AdminOut(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            privileges=json.loads(row["privileges"]),
        )
        for row in rows
    ]


@app.get("/admins/{admin_id}", response_model=AdminOut, tags=["admins"])
def get_admin(admin_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute(
        "SELECT id, username, email, privileges FROM admins WHERE id = ?", (admin_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Admin not found")
    return AdminOut(
        id=row["id"],
        username=row["username"],
        email=row["email"],
        privileges=json.loads(row["privileges"]),
    )


@app.patch("/admins/{admin_id}", response_model=AdminOut, tags=["admins"])
def update_admin(
    admin_id: int, payload: AdminUpdate, db: sqlite3.Connection = Depends(get_db)
):
    fields, params = [], []
    if payload.username is not None:
        fields.append("username = ?")
        params.append(payload.username)
    if payload.email is not None:
        fields.append("email = ?")
        params.append(payload.email)
    if payload.privileges is not None:
        fields.append("privileges = ?")
        params.append(json.dumps(payload.privileges))

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(admin_id)
    try:
        cur = db.cursor()
        cur.execute(f"UPDATE admins SET {', '.join(fields)} WHERE id = ?", params)
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Admin not found")
        db.commit()
        return get_admin(admin_id, db)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Username or email already exists"
        ) from exc


@app.delete("/admins/{admin_id}", tags=["admins"])
def delete_admin(admin_id: int, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Admin not found")
    return {"deleted": True, "id": admin_id}

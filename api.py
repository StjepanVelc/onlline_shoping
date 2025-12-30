from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, List

import sqlite3
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, EmailStr, Field

# ---------- Podesi lokacije ----------
DB_PATH = Path("data/shop.db")
SQL_INIT_FILE = Path("database.sql")  # koristi tvoj SQL ako postoji
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# ---------- Pydantic modeli (Users) ----------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    country: str = Field(..., min_length=2, max_length=50)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    country: Optional[str] = Field(None, min_length=2, max_length=50)


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    country: str


# ---------- Pydantic modeli (Products) ----------
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int


# ---------- Pydantic modeli (Orders) ----------
class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    price: float = Field(..., ge=0)  # snapshot cijene


class OrderCreate(BaseModel):
    user_id: int
    address: str = Field(..., min_length=5, max_length=200)
    items: List[OrderItemIn]


class OrderOut(BaseModel):
    id: int
    user_id: int
    address: str
    status: str
    total_amount: float


# ---------- DB helpers ----------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # SQLite foreign keys:
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def get_db(conn: sqlite3.Connection = Depends(get_connection)):
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Ako postoji database.sql -> izvrši ga.
    Ako ne, napravi minimalnu šemu za users/products/orders/order_items (SQLite).
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        if SQL_INIT_FILE.exists() and SQL_INIT_FILE.read_text(encoding="utf-8").strip():
            cur.executescript(SQL_INIT_FILE.read_text(encoding="utf-8"))
        else:
            cur.executescript(
                """
                PRAGMA foreign_keys=ON;

                CREATE TABLE IF NOT EXISTS users (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email    TEXT NOT NULL UNIQUE,
                    country  TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL CHECK (price >= 0),
                    stock INTEGER NOT NULL CHECK (stock >= 0)
                );

                CREATE TABLE IF NOT EXISTS orders(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  address TEXT NOT NULL,
                  status TEXT NOT NULL DEFAULT 'pending',
                  order_date TEXT NOT NULL DEFAULT (datetime('now')),
                  total_amount REAL,
                  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS order_items(
                  order_id INTEGER NOT NULL,
                  product_id INTEGER NOT NULL,
                  quantity INTEGER NOT NULL CHECK (quantity > 0),
                  price REAL NOT NULL CHECK (price >= 0),
                  PRIMARY KEY(order_id, product_id),
                  FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                  FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE RESTRICT
                );
                """
            )
        conn.commit()
    finally:
        conn.close()


# ---------- Lifespan (umjesto deprecated @on_event) ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Shop API (SQLite quick demo)", lifespan=lifespan)

# ---------- CORS + / -> /docs + favicon ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # DEV: sve dozvoli; u produkciji specificiraj domene
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


# ---------- USERS CRUD ----------
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
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=409, detail="Username or email already exists"
        ) from e


@app.get("/users", response_model=List[UserOut], tags=["users"])
def list_users(
    q: Optional[str] = Query(None, description="Filter po username/email"),
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
    return [UserOut(**dict(r)) for r in rows]


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
    cur = db.cursor()
    cur.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", params)
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    db.commit()
    row = db.execute(
        "SELECT id, username, email, country FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    return UserOut(**dict(row))


@app.delete("/users/{user_id}", tags=["users"])
def delete_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True, "id": user_id}


# ---------- PRODUCTS CRUD ----------
@app.post("/products", response_model=ProductOut, tags=["products"], status_code=201)
def create_product(payload: ProductCreate, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
        (payload.name, payload.description, payload.price, payload.stock),
    )
    db.commit()
    pid = cur.lastrowid
    row = db.execute(
        "SELECT id, name, description, price, stock FROM products WHERE id = ?",
        (pid,),
    ).fetchone()
    return ProductOut(**dict(row))


@app.get("/products", response_model=List[ProductOut], tags=["products"])
def list_products(
    q: Optional[str] = Query(None, description="Filter po nazivu/opisu"),
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
    return [ProductOut(**dict(r)) for r in rows]


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


# ---------- ORDERS: create (transakcija) ----------
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
        oid = cur.lastrowid
        total = 0.0
        for it in payload.items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (oid, it.product_id, it.quantity, it.price),
            )
            total += it.quantity * it.price
        cur.execute("UPDATE orders SET total_amount = ? WHERE id = ?", (total, oid))
        db.commit()
        row = db.execute(
            "SELECT id, user_id, address, status, total_amount FROM orders WHERE id = ?",
            (oid,),
        ).fetchone()
        return OrderOut(**dict(row))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Order failed: {e}")

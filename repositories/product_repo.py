from typing import Dict, List, Optional


class ProductRepository:
    """SQLite data access for products."""

    def __init__(self, db_connection, *, autocommit: bool = True):
        self.db = db_connection
        self.autocommit = autocommit

    def _maybe_commit(self):
        if self.autocommit:
            self.db.commit()

    def _maybe_rollback(self):
        if self.autocommit:
            self.db.rollback()

    @staticmethod
    def _row_to_dict(row) -> Optional[Dict]:
        return dict(row) if row else None

    def create_product(
        self, name: str, description: Optional[str], price: float, stock: int
    ) -> int:
        try:
            cur = self.db.execute(
                "INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
                (name, description, price, stock),
            )
            self._maybe_commit()
            return int(cur.lastrowid)
        except Exception:
            self._maybe_rollback()
            raise

    def list_products(self, q: Optional[str], limit: int, offset: int) -> List[Dict]:
        sql = "SELECT id, name, description, price, stock FROM products"
        params = []
        if q:
            sql += " WHERE name LIKE ? OR description LIKE ?"
            like = f"%{q}%"
            params.extend([like, like])
        sql += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.db.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        row = self.db.execute(
            "SELECT id, name, description, price, stock FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        return self._row_to_dict(row)

    def update_product(self, product_id: int, fields: Dict) -> bool:
        if not fields:
            return False
        set_clause = ", ".join(f"{col} = ?" for col in fields)
        params = list(fields.values()) + [product_id]
        try:
            cur = self.db.execute(
                f"UPDATE products SET {set_clause} WHERE id = ?",
                params,
            )
            self._maybe_commit()
            return cur.rowcount > 0
        except Exception:
            self._maybe_rollback()
            raise

    def adjust_stock(self, product_id: int, delta: int) -> bool:
        try:
            cur = self.db.execute(
                """
                UPDATE products
                SET stock = stock + ?
                WHERE id = ?
                  AND stock + ? >= 0
                """,
                (delta, product_id, delta),
            )
            self._maybe_commit()
            return cur.rowcount > 0
        except Exception:
            self._maybe_rollback()
            raise

    def delete_product(self, product_id: int) -> bool:
        try:
            cur = self.db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self._maybe_commit()
            return cur.rowcount > 0
        except Exception:
            self._maybe_rollback()
            raise

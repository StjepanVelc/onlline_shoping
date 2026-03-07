from typing import Any, List, Optional, Tuple


class ProductRepository:
    """Repository for the SQLite `products` table."""

    def __init__(self, db_connection, *, autocommit: bool = True):
        self.db = db_connection
        self.autocommit = autocommit

    def _maybe_commit(self):
        if self.autocommit:
            self.db.commit()

    def _maybe_rollback(self):
        if self.autocommit:
            self.db.rollback()

    # ---------- READ ----------

    def get_product_by_id(self, product_id: int) -> Optional[Tuple[Any, ...]]:
        """Return product by id as tuple (id, name, price, stock) or None."""
        row = self.db.execute(
            "SELECT id, name, price, stock FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        return tuple(row) if row else None

    def list_products(
        self, *, limit: int = 50, offset: int = 0
    ) -> List[Tuple[Any, ...]]:
        """List products with pagination."""
        rows = self.db.execute(
            "SELECT id, name, price, stock FROM products ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [tuple(row) for row in rows]

    # ---------- WRITE ----------

    def add_product(
        self, name: str, price: float, stock: int, description: Optional[str] = None
    ) -> int:
        """Create a product and return the newly created id."""
        try:
            cur = self.db.execute(
                "INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
                (name, description, price, stock),
            )
            new_id = int(cur.lastrowid)
            self._maybe_commit()
            return new_id
        except Exception:
            self._maybe_rollback()
            raise

    def update_product_stock(self, product_id: int, new_stock: int) -> bool:
        """Set absolute stock and return True if a row was changed."""
        try:
            cur = self.db.execute(
                "UPDATE products SET stock = ? WHERE id = ?",
                (new_stock, product_id),
            )
            updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

    def adjust_stock(self, product_id: int, delta: int) -> bool:
        """Adjust stock by delta without allowing negative stock."""
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
            updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

    def update_product_price(self, product_id: int, new_price: float) -> bool:
        """Update product price and return True if a row was changed."""
        try:
            cur = self.db.execute(
                "UPDATE products SET price = ? WHERE id = ?",
                (new_price, product_id),
            )
            updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

    def delete_product(self, product_id: int) -> bool:
        """Delete product and return True if a row was deleted."""
        try:
            cur = self.db.execute(
                "DELETE FROM products WHERE id = ?",
                (product_id,),
            )
            deleted = cur.rowcount > 0
            self._maybe_commit()
            return deleted
        except Exception:
            self._maybe_rollback()
            raise

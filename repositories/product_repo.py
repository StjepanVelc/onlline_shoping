from typing import Optional, Tuple, Any, List


class ProductRepository:
    """
    Repozitorij za tabelu `products`.

    Kolone (preporučeno):
      id SERIAL PRIMARY KEY
      name VARCHAR(200) NOT NULL
      price NUMERIC(12,2) NOT NULL CHECK (price >= 0)
      stock INTEGER NOT NULL CHECK (stock >= 0)

    Parametar:
      autocommit (bool): True  -> svaka metoda sama radi commit/rollback
                         False -> commit/rollback radi pozivatelj
    """

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
        """
        Vrati proizvod po ID-u (id, name, price, stock) ili None.
        """
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT id, name, price, stock FROM products WHERE id = %s",
                (product_id,),
            )
            return cur.fetchone()

    def list_products(
        self, *, limit: int = 50, offset: int = 0
    ) -> List[Tuple[Any, ...]]:
        """
        Lista proizvode sa paginacijom.
        """
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT id, name, price, stock FROM products ORDER BY id LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return cur.fetchall()

    # ---------- WRITE ----------

    def add_product(self, name: str, price: float, stock: int) -> int:
        """
        Dodaje proizvod i vraća novi id.
        """
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) RETURNING id",
                    (name, price, stock),
                )
                new_id = cur.fetchone()[0]
            self._maybe_commit()
            return new_id
        except Exception:
            self._maybe_rollback()
            raise

    def update_product_stock(self, product_id: int, new_stock: int) -> bool:
        """
        Postavlja apsolutni stock; vraća True ako je promijenjeno.
        """
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "UPDATE products SET stock = %s WHERE id = %s",
                    (new_stock, product_id),
                )
                updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

    def adjust_stock(self, product_id: int, delta: int) -> bool:
        """
        Povećava/smanjuje stock za delta. Negativan delta smanjuje.
        Ne dopušta negativan stock.
        """
        try:
            with self.db.cursor() as cur:
                # Atomicna provjera da ne ode ispod nule
                cur.execute(
                    """
                    UPDATE products
                    SET stock = stock + %s
                    WHERE id = %s
                      AND stock + %s >= 0
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
        """
        Ažurira cijenu; vraća True ako je promijenjeno.
        """
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "UPDATE products SET price = %s WHERE id = %s",
                    (new_price, product_id),
                )
                updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

    def delete_product(self, product_id: int) -> bool:
        """
        Briše proizvod; vraća True ako je red obrisan.
        """
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "DELETE FROM products WHERE id = %s",
                    (product_id,),
                )
                deleted = cur.rowcount > 0
            self._maybe_commit()
            return deleted
        except Exception:
            self._maybe_rollback()
            raise

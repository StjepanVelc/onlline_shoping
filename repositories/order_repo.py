from typing import Dict, Optional


class OrderRepository:
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

    def create_order(self, *, user_id: int, address: str, status: str = "pending") -> int:
        try:
            cur = self.db.execute(
                """
                INSERT INTO orders (user_id, address, status)
                VALUES (?, ?, ?)
                """,
                (user_id, address, status),
            )
            order_id = int(cur.lastrowid)
            self._maybe_commit()
            return order_id
        except Exception:
            self._maybe_rollback()
            raise

    def add_order_item(
        self,
        *,
        order_id: int,
        product_id: int,
        quantity: int,
        price: float,
    ) -> None:
        self.db.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, product_id, quantity, price),
        )

    def update_order_total(self, order_id: int, total_amount: float) -> None:
        self.db.execute(
            "UPDATE orders SET total_amount = ? WHERE id = ?",
            (total_amount, order_id),
        )

    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        row = self.db.execute(
            """
            SELECT id, user_id, address, status, total_amount
            FROM orders
            WHERE id = ?
            """,
            (order_id,),
        ).fetchone()
        return self._row_to_dict(row)

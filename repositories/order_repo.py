from typing import Optional
from models.order import Order


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

    def create_order(self, order: Order) -> int:
        """
        Kreira order (bez stavki) i vraća novi order_id.
        """
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO orders (user_id, address, status)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (order.user_id, order.address, order.status),
                )
                order_id = cur.fetchone()[0]
            self._maybe_commit()
            return order_id
        except Exception:
            self._maybe_rollback()
            raise

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

    def create_order(self, *, user_id: int, address: str, status: str = "pending") -> int:
        """
        Kreira order (bez stavki) i vraca novi order_id.
        """
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

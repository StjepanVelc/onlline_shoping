from typing import Optional, Tuple, Any, List
import json


class AdminRepo:
    def __init__(self, db, *, autocommit: bool = True):
        self.db = db
        self.autocommit = autocommit

    def _maybe_commit(self):
        if self.autocommit:
            self.db.commit()

    def _maybe_rollback(self):
        if self.autocommit:
            self.db.rollback()

    # ---------- READ ----------

    def get_admin_by_id(self, admin_id: int) -> Optional[Tuple[Any, ...]]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, privileges FROM admins WHERE id = %s",
                (admin_id,),
            )
            row = cur.fetchone()
            if row and isinstance(row[3], str):
                # ako je privileges slučajno TEXT, parsiraj
                try:
                    row = (row[0], row[1], row[2], json.loads(row[3]))
                except Exception:
                    pass
            return row

    def get_admin_by_username(self, username: str) -> Optional[Tuple[Any, ...]]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, privileges FROM admins WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
            if row and isinstance(row[3], str):
                try:
                    row = (row[0], row[1], row[2], json.loads(row[3]))
                except Exception:
                    pass
            return row

    # ---------- WRITE ----------

    def create_admin(self, username: str, email: str, privileges: List[str]) -> int:
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "INSERT INTO admins (username, email, privileges) VALUES (%s, %s, %s) RETURNING id",
                    (username, email, json.dumps(privileges)),
                )
                new_id = cur.fetchone()[0]
            self._maybe_commit()
            return new_id
        except Exception:
            self._maybe_rollback()
            raise

    def update_admin_privileges(self, admin_id: int, new_privileges: List[str]) -> bool:
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "UPDATE admins SET privileges = %s WHERE id = %s",
                    (json.dumps(new_privileges), admin_id),
                )
                updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

    def delete_admin(self, admin_id: int) -> bool:
        try:
            with self.db.cursor() as cur:
                cur.execute("DELETE FROM admins WHERE id = %s", (admin_id,))
                deleted = cur.rowcount > 0
            self._maybe_commit()
            return deleted
        except Exception:
            self._maybe_rollback()
            raise

    def protect_privileges(self, admin_id: int) -> bool:
        # zaključaj privilegije na sentinel vrijednost
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "UPDATE admins SET privileges = %s WHERE id = %s",
                    (json.dumps(["protected"]), admin_id),
                )
                updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

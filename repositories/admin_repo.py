from typing import Any, List, Optional, Tuple
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

    @staticmethod
    def _decode_privileges(value: Any) -> List[str]:
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except Exception:
                pass
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    # ---------- READ ----------

    def get_admin_by_id(self, admin_id: int) -> Optional[Tuple[Any, ...]]:
        row = self.db.execute(
            "SELECT id, username, email, privileges FROM admins WHERE id = ?",
            (admin_id,),
        ).fetchone()
        if not row:
            return None
        return (row[0], row[1], row[2], self._decode_privileges(row[3]))

    def get_admin_by_username(self, username: str) -> Optional[Tuple[Any, ...]]:
        row = self.db.execute(
            "SELECT id, username, email, privileges FROM admins WHERE username = ?",
            (username,),
        ).fetchone()
        if not row:
            return None
        return (row[0], row[1], row[2], self._decode_privileges(row[3]))

    # ---------- WRITE ----------

    def create_admin(self, username: str, email: str, privileges: List[str]) -> int:
        try:
            cur = self.db.execute(
                "INSERT INTO admins (username, email, privileges) VALUES (?, ?, ?)",
                (username, email, json.dumps(privileges)),
            )
            new_id = int(cur.lastrowid)
            self._maybe_commit()
            return new_id
        except Exception:
            self._maybe_rollback()
            raise

    def update_admin_privileges(self, admin_id: int, new_privileges: List[str]) -> bool:
        try:
            cur = self.db.execute(
                "UPDATE admins SET privileges = ? WHERE id = ?",
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
            cur = self.db.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
            deleted = cur.rowcount > 0
            self._maybe_commit()
            return deleted
        except Exception:
            self._maybe_rollback()
            raise

    def protect_privileges(self, admin_id: int) -> bool:
        # Lock privileges to a sentinel value.
        try:
            cur = self.db.execute(
                "UPDATE admins SET privileges = ? WHERE id = ?",
                (json.dumps(["protected"]), admin_id),
            )
            updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

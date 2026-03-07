from typing import Dict, List, Optional


class UserRepository:
    """SQLite data access for users."""

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

    def create_user(self, username: str, email: str, country: str) -> int:
        try:
            cur = self.db.execute(
                "INSERT INTO users (username, email, country) VALUES (?, ?, ?)",
                (username, email, country),
            )
            self._maybe_commit()
            return int(cur.lastrowid)
        except Exception:
            self._maybe_rollback()
            raise

    def list_users(self, q: Optional[str], limit: int, offset: int) -> List[Dict]:
        sql = "SELECT id, username, email, country FROM users"
        params = []
        if q:
            sql += " WHERE username LIKE ? OR email LIKE ?"
            like = f"%{q}%"
            params.extend([like, like])
        sql += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.db.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        row = self.db.execute(
            "SELECT id, username, email, country FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return self._row_to_dict(row)

    def update_user(self, user_id: int, fields: Dict) -> bool:
        if not fields:
            return False
        set_clause = ", ".join(f"{col} = ?" for col in fields)
        params = list(fields.values()) + [user_id]
        try:
            cur = self.db.execute(
                f"UPDATE users SET {set_clause} WHERE id = ?",
                params,
            )
            self._maybe_commit()
            return cur.rowcount > 0
        except Exception:
            self._maybe_rollback()
            raise

    def delete_user(self, user_id: int) -> bool:
        try:
            cur = self.db.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self._maybe_commit()
            return cur.rowcount > 0
        except Exception:
            self._maybe_rollback()
            raise

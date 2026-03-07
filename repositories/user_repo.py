from typing import Any, Optional, Tuple


class UserRepository:
    """Repository for the SQLite `users` table."""

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

    def get_user_by_id(self, user_id: int) -> Optional[Tuple[Any, ...]]:
        """Return user by id as tuple (id, username, email, country) or None."""
        row = self.db.execute(
            "SELECT id, username, email, country FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return tuple(row) if row else None

    def get_user_by_username(self, username: str) -> Optional[Tuple[Any, ...]]:
        row = self.db.execute(
            "SELECT id, username, email, country FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return tuple(row) if row else None

    # ---------- WRITE ----------

    def create_user(self, username: str, email: str, country: str = "Unknown") -> int:
        """Create a user and return the newly created id."""
        try:
            cur = self.db.execute(
                "INSERT INTO users (username, email, country) VALUES (?, ?, ?)",
                (username, email, country),
            )
            new_id = int(cur.lastrowid)
            self._maybe_commit()
            return new_id
        except Exception:
            self._maybe_rollback()
            raise

    def update_user_email(self, user_id: int, new_email: str) -> bool:
        """Update user email; returns True when a row is changed."""
        try:
            cur = self.db.execute(
                "UPDATE users SET email = ? WHERE id = ?",
                (new_email, user_id),
            )
            updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

    def delete_user(self, user_id: int) -> bool:
        """Delete user; returns True when a row is deleted."""
        try:
            cur = self.db.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,),
            )
            deleted = cur.rowcount > 0
            self._maybe_commit()
            return deleted
        except Exception:
            self._maybe_rollback()
            raise

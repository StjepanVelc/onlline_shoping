from typing import Any, Dict, List, Optional
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

    def _row_to_public_dict(self, row) -> Optional[Dict]:
        if not row:
            return None
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "privileges": self._decode_privileges(row["privileges"]),
        }

    def count_admins(self) -> int:
        row = self.db.execute("SELECT COUNT(*) AS cnt FROM admins").fetchone()
        return int(row["cnt"]) if row else 0

    def create_admin(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
        privileges: List[str],
    ) -> int:
        try:
            cur = self.db.execute(
                """
                INSERT INTO admins (username, email, password_hash, privileges)
                VALUES (?, ?, ?, ?)
                """,
                (username, email, password_hash, json.dumps(privileges)),
            )
            self._maybe_commit()
            return int(cur.lastrowid)
        except Exception:
            self._maybe_rollback()
            raise

    def list_admins(self, q: Optional[str], limit: int, offset: int) -> List[Dict]:
        sql = "SELECT id, username, email, privileges FROM admins"
        params = []
        if q:
            sql += " WHERE username LIKE ? OR email LIKE ?"
            like = f"%{q}%"
            params.extend([like, like])
        sql += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.db.execute(sql, params).fetchall()
        return [self._row_to_public_dict(row) for row in rows]

    def get_admin_by_id(self, admin_id: int) -> Optional[Dict]:
        row = self.db.execute(
            "SELECT id, username, email, privileges FROM admins WHERE id = ?",
            (admin_id,),
        ).fetchone()
        return self._row_to_public_dict(row)

    def get_admin_auth_by_username(self, username: str) -> Optional[Dict]:
        row = self.db.execute(
            """
            SELECT id, username, email, password_hash, privileges
            FROM admins
            WHERE username = ?
            """,
            (username,),
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "password_hash": row["password_hash"],
            "privileges": self._decode_privileges(row["privileges"]),
        }

    def update_admin(self, admin_id: int, fields: Dict) -> bool:
        if not fields:
            return False
        normalized = dict(fields)
        if "privileges" in normalized:
            normalized["privileges"] = json.dumps(normalized["privileges"])
        set_clause = ", ".join(f"{col} = ?" for col in normalized)
        params = list(normalized.values()) + [admin_id]
        try:
            cur = self.db.execute(
                f"UPDATE admins SET {set_clause} WHERE id = ?",
                params,
            )
            self._maybe_commit()
            return cur.rowcount > 0
        except Exception:
            self._maybe_rollback()
            raise

    def delete_admin(self, admin_id: int) -> bool:
        try:
            cur = self.db.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
            self._maybe_commit()
            return cur.rowcount > 0
        except Exception:
            self._maybe_rollback()
            raise

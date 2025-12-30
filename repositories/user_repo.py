from typing import Optional, Tuple, Any


class UserRepository:
    """
    Repozitorij za tabelu `users`.

    Očekuje konekciju kompatibilnu sa psycopg2:
      - conn.cursor() kao context manager
      - cursor.execute(sql, params)
      - cursor.fetchone(), cursor.rowcount
      - conn.commit(), conn.rollback()

    Parametar:
      autocommit (bool): True  -> svaka metoda sama radi commit/rollback
                         False -> commit/rollback radi pozivatelj (service layer)
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

    def get_user_by_id(self, user_id: int) -> Optional[Tuple[Any, ...]]:
        """
        Vrati korisnika po ID-u (id, username, email) ili None ako ne postoji.
        Ako želiš dict umjesto tuple-a, kreiraj konekciju sa RealDictCursor.
        """
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT id, username, email FROM users WHERE id = %s",
                (user_id,),
            )
            return cur.fetchone()

    def get_user_by_username(self, username: str) -> Optional[Tuple[Any, ...]]:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT id, username, email FROM users WHERE username = %s",
                (username,),
            )
            return cur.fetchone()

    # ---------- WRITE ----------

    def create_user(self, username: str, email: str) -> int:
        """
        Kreira korisnika i vraća novi id.
        """
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id",
                    (username, email),
                )
                new_id = cur.fetchone()[0]
            self._maybe_commit()
            return new_id
        except Exception:
            self._maybe_rollback()
            raise

    def update_user_email(self, user_id: int, new_email: str) -> bool:
        """
        Ažurira email; vraća True ako je išta promijenjeno.
        """
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "UPDATE users SET email = %s WHERE id = %s",
                    (new_email, user_id),
                )
                updated = cur.rowcount > 0
            self._maybe_commit()
            return updated
        except Exception:
            self._maybe_rollback()
            raise

    def delete_user(self, user_id: int) -> bool:
        """
        Briše korisnika; vraća True ako je red obrisan.
        """
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    "DELETE FROM users WHERE id = %s",
                    (user_id,),
                )
                deleted = cur.rowcount > 0
            self._maybe_commit()
            return deleted
        except Exception:
            self._maybe_rollback()
            raise

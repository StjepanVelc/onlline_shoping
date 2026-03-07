import sqlite3
from typing import Dict, List, Optional

from repositories.user_repo import UserRepository
from services.exceptions import ConflictError, NotFoundError, ValidationError


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, payload) -> Dict:
        try:
            user_id = self.repo.create_user(payload.username, payload.email, payload.country)
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Username or email already exists") from exc
        created = self.repo.get_user_by_id(user_id)
        return created

    def list_users(self, q: Optional[str], limit: int, offset: int) -> List[Dict]:
        return self.repo.list_users(q=q, limit=limit, offset=offset)

    def get_user(self, user_id: int) -> Dict:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def update_user(self, user_id: int, payload) -> Dict:
        fields = {
            key: value
            for key, value in payload.model_dump().items()
            if value is not None
        }
        if not fields:
            raise ValidationError("No fields to update")
        try:
            updated = self.repo.update_user(user_id, fields)
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Username or email already exists") from exc
        if not updated:
            raise NotFoundError("User not found")
        return self.get_user(user_id)

    def delete_user(self, user_id: int) -> Dict:
        deleted = self.repo.delete_user(user_id)
        if not deleted:
            raise NotFoundError("User not found")
        return {"deleted": True, "id": user_id}

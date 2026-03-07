import sqlite3
from typing import Dict, List, Optional

from repositories.admin_repo import AdminRepo
from services.auth_service import hash_password
from services.exceptions import ConflictError, NotFoundError, ValidationError


class AdminService:
    def __init__(self, repo: AdminRepo):
        self.repo = repo

    def create_admin(self, payload) -> Dict:
        try:
            admin_id = self.repo.create_admin(
                username=payload.username,
                email=payload.email,
                password_hash=hash_password(payload.password),
                privileges=payload.privileges,
            )
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Username or email already exists") from exc
        return self.get_admin(admin_id)

    def list_admins(self, q: Optional[str], limit: int, offset: int) -> List[Dict]:
        return self.repo.list_admins(q=q, limit=limit, offset=offset)

    def get_admin(self, admin_id: int) -> Dict:
        admin = self.repo.get_admin_by_id(admin_id)
        if not admin:
            raise NotFoundError("Admin not found")
        return admin

    def update_admin(self, admin_id: int, payload) -> Dict:
        fields = {
            key: value
            for key, value in payload.model_dump().items()
            if value is not None
        }
        if not fields:
            raise ValidationError("No fields to update")
        if "password" in fields:
            fields["password_hash"] = hash_password(fields.pop("password"))
        try:
            updated = self.repo.update_admin(admin_id, fields)
        except sqlite3.IntegrityError as exc:
            raise ConflictError("Username or email already exists") from exc
        if not updated:
            raise NotFoundError("Admin not found")
        return self.get_admin(admin_id)

    def delete_admin(self, admin_id: int) -> Dict:
        deleted = self.repo.delete_admin(admin_id)
        if not deleted:
            raise NotFoundError("Admin not found")
        return {"deleted": True, "id": admin_id}

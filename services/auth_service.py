import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from jose import JWTError, jwt

from repositories.admin_repo import AdminRepo
from services.exceptions import AuthError, ValidationError

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, expected = password_hash.split("$", 1)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()
    return secrets.compare_digest(digest, expected)


def create_access_token(data: Dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class AuthService:
    def __init__(self, repo: AdminRepo):
        self.repo = repo

    def bootstrap_admin(self, payload) -> Dict:
        if self.repo.count_admins() > 0:
            raise ValidationError("Bootstrap is only allowed when there are no admins")
        admin_id = self.repo.create_admin(
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
            privileges=payload.privileges or ["super_admin"],
        )
        admin = self.repo.get_admin_by_id(admin_id)
        return admin

    def login(self, username: str, password: str) -> Dict:
        admin = self.repo.get_admin_auth_by_username(username)
        if not admin or not verify_password(password, admin.get("password_hash", "")):
            raise AuthError("Incorrect username or password")
        token = create_access_token(
            {
                "sub": admin["username"],
                "admin_id": admin["id"],
            }
        )
        return {"access_token": token, "token_type": "bearer"}

    def current_admin_from_token(self, token: str) -> Dict:
        credentials_exception = AuthError("Could not validate credentials")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: Optional[str] = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError as exc:
            raise credentials_exception from exc

        admin = self.repo.get_admin_auth_by_username(username)
        if not admin:
            raise credentials_exception
        return {
            "id": admin["id"],
            "username": admin["username"],
            "email": admin["email"],
            "privileges": admin["privileges"],
        }

from dataclasses import dataclass, field
from typing import List
from email.utils import parseaddr


@dataclass
class Admin:
    id: int
    username: str
    email: str
    privileges: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.username = (self.username or "").strip()
        self.email = (self.email or "").strip()
        if not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("ID must be a positive integer.")
        if len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if not parseaddr(self.email)[1]:
            raise ValueError("Invalid email address.")
        if not isinstance(self.privileges, list) or not all(
            isinstance(p, str) for p in self.privileges
        ):
            raise ValueError("Privileges must be a list of strings.")

    # helpers
    def add_privilege(self, privilege: str) -> None:
        if privilege not in self.privileges:
            self.privileges.append(privilege)

    def remove_privilege(self, privilege: str) -> None:
        if privilege in self.privileges:
            self.privileges.remove(privilege)

    def has_privilege(self, privilege: str) -> bool:
        return privilege in self.privileges

    def display_admin_info(self) -> str:
        return f"Admin ID: {self.id}, Username: {self.username}, Email: {self.email}, Privileges: {', '.join(self.privileges)}"

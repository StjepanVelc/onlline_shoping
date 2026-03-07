from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    privileges: List[str] = Field(default_factory=list, description="Lista privilegija (npr. ['manage_users', 'manage_products'])")


class AdminUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    privileges: Optional[List[str]] = None


class AdminOut(BaseModel):
    id: int
    username: str
    email: str
    privileges: List[str]

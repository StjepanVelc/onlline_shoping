from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    privileges: List[str] = Field(
        default_factory=list,
        description="Lista privilegija (npr. ['manage_users', 'manage_products'])",
    )


class AdminUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    privileges: Optional[List[str]] = None


class AdminOut(BaseModel):
    id: int
    username: str
    email: str
    privileges: List[str]


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

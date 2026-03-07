from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    country: str = Field(..., min_length=2, max_length=50)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    country: Optional[str] = Field(None, min_length=2, max_length=50)


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    country: str
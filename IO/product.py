import re
from typing import List, Literal, Optional, overload

from pydantic import BaseModel, Field, field_validator


@overload
def _clean_text(
    value: Optional[str],
    field_name: str,
    *,
    allow_empty: Literal[False],
) -> str: ...


@overload
def _clean_text(
    value: Optional[str],
    field_name: str,
    *,
    allow_empty: Literal[True],
) -> Optional[str]: ...


def _clean_text(
    value: Optional[str],
    field_name: str,
    *,
    allow_empty: bool,
) -> Optional[str]:
    if value is None:
        if not allow_empty:
            raise ValueError(f"{field_name} is required")
        return None

    cleaned = value.strip()
    # Normalize multiple spaces to single space (e.g., "t  e  s  t" -> "t e s t")
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    if not cleaned:
        if allow_empty:
            return None
        raise ValueError(f"{field_name} cannot be blank")

    if "<" in cleaned or ">" in cleaned:
        raise ValueError(f"{field_name} cannot contain HTML tags")

    # Only allow alphanumeric, spaces, hyphens, parentheses, and dots
    if not re.match(r"^[a-zA-Z0-9\s\-().,&+]+$", cleaned):
        raise ValueError(f"{field_name} contains invalid characters")

    # Ensure at least one letter (not just numbers)
    if not re.search(r"[a-zA-Z]", cleaned):
        raise ValueError(f"{field_name} must contain at least one letter")

    return cleaned


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=20)
    description: Optional[str] = None
    price: float = Field(..., ge=0.01, le=999999.99)
    stock: int = Field(..., ge=0, le=999999)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _clean_text(value, "name", allow_empty=False)

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value, "description", allow_empty=True)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=20)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0.01, le=999999.99)
    stock: Optional[int] = Field(None, ge=0, le=999999)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value, "name", allow_empty=False)

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value, "description", allow_empty=True)


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    user_id: int
    address: str = Field(..., min_length=5, max_length=200)
    items: List[OrderItemIn]


class OrderOut(BaseModel):
    id: int
    user_id: int
    address: str
    status: str
    total_amount: float
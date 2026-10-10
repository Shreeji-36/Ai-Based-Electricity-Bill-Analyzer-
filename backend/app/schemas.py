from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    email: str = Field(max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=64)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserOut(BaseModel):
    email: str
    name: str
    role: Literal["admin", "analyst", "viewer"]


class Bill(BaseModel):
    consumer_number: str | None = Field(default=None, max_length=30)
    billing_date: str | None = Field(default=None, max_length=20)
    tariff: str | None = Field(default=None, max_length=40)
    units: float = Field(gt=0, le=10_000_000)
    amount: float = Field(gt=0, le=1_000_000_000)
    days: int = Field(default=30, ge=1, le=62)


class AnalysisIn(BaseModel):
    industry: Literal["pharmacy", "dairy", "steel", "coldstorage"]
    bill: Bill
    hours: dict[str, float]
    qty: dict[str, int] = Field(default_factory=dict)

    @field_validator("hours")
    @classmethod
    def check_hours(cls, v: dict[str, float]):
        for key, h in v.items():
            if not 0 <= h <= 24:
                raise ValueError(f"Hours for '{key}' must be between 0 and 24")
        return v

    @field_validator("qty")
    @classmethod
    def check_qty(cls, v: dict[str, int]):
        for key, n in v.items():
            if not 0 <= n <= 5000:
                raise ValueError(f"Quantity for '{key}' must be between 0 and 5000")
        return v
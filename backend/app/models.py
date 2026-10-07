from datetime import datetime, timezone
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(60))
    password_hash: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default="analyst")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Bill(Base):
    __tablename__ = "bills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    industry: Mapped[str] = mapped_column(String(20), index=True)
    consumer_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    billing_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tariff: Mapped[str | None] = mapped_column(String(40), nullable=True)
    units: Mapped[float] = mapped_column(Float)
    amount: Mapped[float] = mapped_column(Float)
    days: Mapped[int] = mapped_column(Integer, default=30)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey("bills.id"))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
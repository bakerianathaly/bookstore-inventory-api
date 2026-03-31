import re
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


# ─── Modelo DB ───────────────────────────────────────────────
class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    author: str = Field(max_length=255)
    isbn: str = Field(max_length=20, unique=True, nullable=False)
    cost_usd: Decimal = Field(max_digits=10, decimal_places=2)
    selling_price_local: Optional[Decimal] = Field(
        default=None, max_digits=12, decimal_places=2
    )
    stock_quantity: int = Field(default=0)
    category: str = Field(max_length=255)
    supplier_country: str = Field(max_length=5)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ─── Schemas API ─────────────────────────────────────────────
class BookCreate(SQLModel):
    title: str = Field(max_length=255)
    author: str = Field(max_length=255)
    isbn: str = Field(max_length=20)
    cost_usd: Decimal = Field(max_digits=10, decimal_places=2)
    stock_quantity: int = Field(default=0)
    category: str = Field(max_length=255)
    supplier_country: str = Field(max_length=5)


class BookUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=255)
    author: Optional[str] = Field(default=None, max_length=255)
    isbn: Optional[str] = Field(default=None, max_length=20)
    cost_usd: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    stock_quantity: Optional[int] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=255)
    supplier_country: Optional[str] = Field(default=None, max_length=5)


class BookResponse(SQLModel):
    id: int
    title: str
    author: str
    isbn: str
    cost_usd: Decimal
    selling_price_local: Optional[Decimal]
    stock_quantity: int
    category: str
    supplier_country: str
    created_at: datetime
    updated_at: datetime


class PriceCalculationResponse(SQLModel):
    book_id: int
    cost_usd: Decimal
    exchange_rate: Decimal
    cost_local: Decimal
    margin_percentage: int = 40
    selling_price_local: Decimal
    currency: str = "VES"
    calculation_timestamp: datetime

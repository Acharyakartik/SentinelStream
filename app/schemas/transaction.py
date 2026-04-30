from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class TransactionCreate(BaseModel):
    user_id: str = Field(min_length=3, max_length=64)
    merchant_id: str = Field(min_length=3, max_length=64)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3, default="USD")
    country: str = Field(min_length=2, max_length=2)

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return value.upper()

    @field_validator("country")
    @classmethod
    def uppercase_country(cls, value: str) -> str:
        return value.upper()


class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    risk_score: float
    triggered_rules: list[str]
    created_at: datetime


class BalanceResponse(BaseModel):
    user_id: str
    current_balance: Decimal


class TransactionHistoryItem(BaseModel):
    transaction_id: str
    merchant_id: str
    amount: Decimal
    currency: str
    status: str
    risk_score: float
    created_at: datetime

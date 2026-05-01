from datetime import datetime

from pydantic import BaseModel, Field


class FraudRuleCreate(BaseModel):
    name: str = Field(min_length=3, max_length=128)
    expression: str = Field(min_length=3)
    risk_weight: float = Field(ge=0.0, le=1.0, default=0.15)
    enabled: bool = True


class FraudRuleResponse(FraudRuleCreate):
    id: int
    created_at: datetime

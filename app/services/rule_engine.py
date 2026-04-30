from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FraudRule, UserProfile
from app.schemas import TransactionCreate


@dataclass
class RuleEvaluationResult:
    triggered_rules: list[str]
    combined_weight: float


class RuleEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate(self, payload: TransactionCreate, user: UserProfile) -> RuleEvaluationResult:
        rules = (
            await self.db.execute(select(FraudRule).where(FraudRule.enabled.is_(True)))
        ).scalars().all()

        context: dict[str, Any] = {
            "amount": float(payload.amount),
            "country": payload.country,
            "user_home_country": user.home_country,
            "balance": float(user.current_balance),
        }
        triggered: list[str] = []
        weight = 0.0

        for rule in rules:
            if self._eval_expression(rule.expression, context):
                triggered.append(rule.name)
                weight += float(rule.risk_weight)

        return RuleEvaluationResult(triggered_rules=triggered, combined_weight=min(weight, 1.0))

    @staticmethod
    def _eval_expression(expression: str, context: dict[str, Any]) -> bool:
        safe_globals = {"__builtins__": {}}
        try:
            return bool(eval(expression, safe_globals, context))
        except Exception:
            return False

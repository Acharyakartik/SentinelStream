from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_token
from app.db.session import get_db
from app.models import FraudRule
from app.schemas import FraudRuleCreate, FraudRuleResponse

router = APIRouter(prefix="/v1/rules", tags=["rules"])


@router.post("", response_model=FraudRuleResponse, status_code=201)
async def create_rule(
    payload: FraudRuleCreate, db: AsyncSession = Depends(get_db), _: str = Depends(require_token)
) -> FraudRuleResponse:
    existing = (await db.execute(select(FraudRule).where(FraudRule.name == payload.name))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rule name already exists.")

    rule = FraudRule(**payload.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return FraudRuleResponse(
        id=rule.id,
        name=rule.name,
        expression=rule.expression,
        risk_weight=rule.risk_weight,
        enabled=rule.enabled,
        created_at=rule.created_at,
    )


@router.get("", response_model=list[FraudRuleResponse])
async def list_rules(db: AsyncSession = Depends(get_db), _: str = Depends(require_token)) -> list[FraudRuleResponse]:
    rules = (await db.execute(select(FraudRule).order_by(FraudRule.id.desc()))).scalars().all()
    return [
        FraudRuleResponse(
            id=rule.id,
            name=rule.name,
            expression=rule.expression,
            risk_weight=rule.risk_weight,
            enabled=rule.enabled,
            created_at=rule.created_at,
        )
        for rule in rules
    ]

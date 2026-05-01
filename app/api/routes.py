from datetime import datetime

from redis.asyncio import Redis
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Transaction, UserProfile
from app.core.security import require_token
from app.schemas import BalanceResponse, TransactionCreate, TransactionHistoryItem, TransactionResponse
from app.services.fraud_pipeline import FraudPipeline
from app.services.idempotency import build_request_hash, check_existing_record, save_record
from app.services.ledger import LedgerService
from app.services.ml_scorer import MLScorer
from app.services.profile_cache import CachedUserProfile, UserProfileCache
from app.workers.tasks import send_webhook_notification

router = APIRouter(prefix="/v1", tags=["transactions"])
ml_scorer = MLScorer()


async def maybe_rate_limit(request: Request, response: Response) -> None:
    if getattr(request.app.state, "rate_limiter_ready", False):
        await RateLimiter(times=100, seconds=1)(request, response)


def get_profile_cache(request: Request) -> UserProfileCache:
    redis_client: Redis | None = getattr(request.app.state, "redis_client", None)
    return UserProfileCache(redis_client=redis_client)


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_token),
    __: None = Depends(maybe_rate_limit),
    profile_cache: UserProfileCache = Depends(get_profile_cache),
    x_idempotency_key: str = Header(default="", alias="Idempotency-Key"),
) -> TransactionResponse:
    if not x_idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Idempotency-Key header is required.")

    request_hash = build_request_hash(payload.model_dump())
    existing = await check_existing_record(db, x_idempotency_key, request_hash)
    if existing is not None:
        return TransactionResponse(**existing.response_payload)

    fraud = FraudPipeline(db, ml_scorer, profile_cache)
    user_profile = await profile_cache.get_or_create(db, payload.user_id, payload.country)
    final_risk_score, triggered_rules = await fraud.score(payload, profile=user_profile)
    tx_status = "DECLINED" if final_risk_score >= 0.7 else "APPROVED"

    ledger = LedgerService(db, profile_cache)
    tx = await ledger.persist_transaction(
        payload, tx_status, final_risk_score, triggered_rules, profile=user_profile
    )
    await db.flush()

    response_payload = TransactionResponse(
        transaction_id=str(tx.id),
        status=tx.status,
        risk_score=tx.risk_score,
        triggered_rules=triggered_rules,
        created_at=tx.created_at or datetime.utcnow(),
    ).model_dump()
    await save_record(db, x_idempotency_key, request_hash, response_payload, status_code=200)

    await db.commit()

    send_webhook_notification.delay(
        merchant_id=payload.merchant_id,
        transaction_id=str(tx.id),
        status=tx.status,
        risk_score=tx.risk_score,
    )
    return TransactionResponse(**response_payload)


@router.get("/users/{user_id}/balance", response_model=BalanceResponse)
async def get_balance(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_token),
    profile_cache: UserProfileCache = Depends(get_profile_cache),
) -> BalanceResponse:
    cached = await profile_cache.get(user_id)
    if cached is not None:
        return BalanceResponse(user_id=user_id, current_balance=cached.current_balance)

    user = await db.get(UserProfile, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    await profile_cache.set(
        CachedUserProfile(
            user_id=user.id,
            home_country=user.home_country,
            current_balance=user.current_balance,
        )
    )
    return BalanceResponse(user_id=user_id, current_balance=user.current_balance)


@router.get("/users/{user_id}/transactions", response_model=list[TransactionHistoryItem])
async def get_history(
    user_id: str, db: AsyncSession = Depends(get_db), _: str = Depends(require_token)
) -> list[TransactionHistoryItem]:
    rows = (
        await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(desc(Transaction.created_at))
            .limit(100)
        )
    ).scalars().all()

    return [
        TransactionHistoryItem(
            transaction_id=str(row.id),
            merchant_id=row.merchant_id,
            amount=row.amount,
            currency=row.currency,
            status=row.status,
            risk_score=row.risk_score,
            created_at=row.created_at,
        )
        for row in rows
    ]

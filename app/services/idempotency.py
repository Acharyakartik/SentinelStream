import hashlib
import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IdempotencyRecord


def build_request_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


async def check_existing_record(
    db: AsyncSession, idempotency_key: str, request_hash: str
) -> IdempotencyRecord | None:
    record = await db.get(IdempotencyRecord, idempotency_key)
    if record is None:
        return None
    if record.request_hash != request_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency key reused with different payload.",
        )
    return record


async def save_record(
    db: AsyncSession,
    idempotency_key: str,
    request_hash: str,
    response_payload: dict[str, Any],
    status_code: int = 200,
) -> None:
    record = IdempotencyRecord(
        key=idempotency_key,
        request_hash=request_hash,
        response_payload=response_payload,
        status_code=status_code,
    )
    db.add(record)

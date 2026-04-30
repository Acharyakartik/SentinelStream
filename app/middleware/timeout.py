import asyncio
import time

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        timeout_seconds = settings.request_timeout_ms / 1000
        started_at = time.perf_counter()
        try:
            response = await asyncio.wait_for(call_next(request), timeout=timeout_seconds)
        except asyncio.TimeoutError as exc:
            raise HTTPException(status_code=504, detail="Request exceeded max latency budget.") from exc

        response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - started_at) * 1000:.2f}"
        return response

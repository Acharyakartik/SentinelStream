from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from app.api.auth import router as auth_router
from app.api.rules import router as rules_router
from app.api.routes import router as transaction_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.middleware.timeout import RequestTimeoutMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rate_limiter_ready = False
    app.state.redis_client = None
    if settings.auto_create_schema:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    try:
        redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_client)
        app.state.rate_limiter_ready = True
        app.state.redis_client = redis_client
    except Exception:
        # Service still starts if Redis is unavailable in local development.
        pass

    yield
    if app.state.redis_client is not None:
        await app.state.redis_client.close()
    await engine.dispose()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(RequestTimeoutMiddleware)
app.include_router(auth_router)
app.include_router(rules_router)
app.include_router(transaction_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.app_name}

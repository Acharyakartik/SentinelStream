import json
from dataclasses import dataclass
from decimal import Decimal

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserProfile


@dataclass
class CachedUserProfile:
    user_id: str
    home_country: str
    current_balance: Decimal


class UserProfileCache:
    def __init__(self, redis_client: Redis | None, ttl_seconds: int = 300):
        self.redis_client = redis_client
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def _key(user_id: str) -> str:
        return f"user_profile:{user_id}"

    async def get_or_create(self, db: AsyncSession, user_id: str, default_country: str) -> CachedUserProfile:
        cached = await self.get(user_id)
        if cached is not None:
            return cached

        profile = await db.get(UserProfile, user_id)
        if profile is None:
            profile = UserProfile(id=user_id, home_country=default_country, current_balance=Decimal("10000.00"))
            db.add(profile)
            await db.flush()

        cached_profile = CachedUserProfile(
            user_id=profile.id,
            home_country=profile.home_country,
            current_balance=Decimal(profile.current_balance),
        )
        await self.set(cached_profile)
        return cached_profile

    async def get(self, user_id: str) -> CachedUserProfile | None:
        if self.redis_client is None:
            return None

        raw = await self.redis_client.get(self._key(user_id))
        if not raw:
            return None

        data = json.loads(raw)
        return CachedUserProfile(
            user_id=data["user_id"],
            home_country=data["home_country"],
            current_balance=Decimal(str(data["current_balance"])),
        )

    async def set(self, profile: CachedUserProfile) -> None:
        if self.redis_client is None:
            return
        payload = {
            "user_id": profile.user_id,
            "home_country": profile.home_country,
            "current_balance": str(profile.current_balance),
        }
        await self.redis_client.set(self._key(profile.user_id), json.dumps(payload), ex=self.ttl_seconds)

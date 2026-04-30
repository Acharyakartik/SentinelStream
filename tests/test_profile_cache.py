from decimal import Decimal

import pytest

from app.services.profile_cache import CachedUserProfile, UserProfileCache


class FakeRedis:
    def __init__(self):
        self._store = {}

    async def get(self, key: str):
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self._store[key] = value


@pytest.mark.asyncio
async def test_profile_cache_set_and_get():
    cache = UserProfileCache(redis_client=FakeRedis(), ttl_seconds=60)
    profile = CachedUserProfile(user_id="u-1", home_country="US", current_balance=Decimal("99.50"))

    await cache.set(profile)
    loaded = await cache.get("u-1")

    assert loaded is not None
    assert loaded.user_id == "u-1"
    assert loaded.home_country == "US"
    assert loaded.current_balance == Decimal("99.50")

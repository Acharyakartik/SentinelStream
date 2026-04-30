from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Transaction, UserProfile
from app.schemas import TransactionCreate
from app.services.profile_cache import CachedUserProfile, UserProfileCache


class LedgerService:
    def __init__(self, db: AsyncSession, profile_cache: UserProfileCache):
        self.db = db
        self.profile_cache = profile_cache

    async def persist_transaction(
        self,
        payload: TransactionCreate,
        status: str,
        risk_score: float,
        triggered_rules: list[str],
        profile: CachedUserProfile,
    ) -> Transaction:
        user = await self.db.get(UserProfile, payload.user_id)
        if user is None:
            user = UserProfile(
                id=profile.user_id,
                home_country=profile.home_country,
                current_balance=profile.current_balance,
            )
            self.db.add(user)
            await self.db.flush()

        if status == "APPROVED":
            user.current_balance = Decimal(user.current_balance) - payload.amount
            profile.current_balance = Decimal(user.current_balance)
            await self.profile_cache.set(profile)

        tx = Transaction(
            user_id=payload.user_id,
            merchant_id=payload.merchant_id,
            amount=payload.amount,
            currency=payload.currency,
            country=payload.country,
            status=status,
            risk_score=risk_score,
            triggered_rules={"rules": triggered_rules},
        )
        self.db.add(tx)
        return tx

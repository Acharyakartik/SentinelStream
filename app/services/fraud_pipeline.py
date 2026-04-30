from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import TransactionCreate
from app.services.ml_scorer import MLScorer
from app.services.profile_cache import CachedUserProfile, UserProfileCache
from app.services.rule_engine import RuleEngine


class FraudPipeline:
    def __init__(self, db: AsyncSession, ml_scorer: MLScorer, profile_cache: UserProfileCache):
        self.db = db
        self.ml_scorer = ml_scorer
        self.profile_cache = profile_cache
        self.rule_engine = RuleEngine(db)

    async def score(
        self, payload: TransactionCreate, profile: CachedUserProfile | None = None
    ) -> tuple[float, list[str]]:
        user = profile or await self.profile_cache.get_or_create(self.db, payload.user_id, payload.country)

        ml_score = self.ml_scorer.score(payload, user)
        rule_result = await self.rule_engine.evaluate(payload, user)
        final_score = min(1.0, 0.65 * ml_score + 0.35 * rule_result.combined_weight)
        return final_score, rule_result.triggered_rules

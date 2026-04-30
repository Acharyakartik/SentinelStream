from pathlib import Path

import joblib
import numpy as np

from app.core.config import settings
from app.models import UserProfile
from app.schemas import TransactionCreate


class MLScorer:
    def __init__(self) -> None:
        self.model = self._load_model()

    def _load_model(self):
        model_path = Path(settings.ml_model_path)
        if model_path.exists():
            return joblib.load(model_path)
        return None

    def score(self, payload: TransactionCreate, user: UserProfile) -> float:
        if self.model is None:
            return self._fallback_score(payload, user)

        features = np.array(
            [
                [
                    float(payload.amount),
                    1.0 if payload.country != user.home_country else 0.0,
                    float(user.current_balance),
                ]
            ]
        )
        raw = self.model.decision_function(features)[0]
        normalized = 1.0 / (1.0 + np.exp(raw))
        return float(max(0.0, min(normalized, 1.0)))

    @staticmethod
    def _fallback_score(payload: TransactionCreate, user: UserProfile) -> float:
        score = 0.1
        if payload.amount > 5000:
            score += 0.5
        if payload.country != user.home_country:
            score += 0.25
        if payload.amount > user.current_balance:
            score += 0.2
        return min(score, 1.0)

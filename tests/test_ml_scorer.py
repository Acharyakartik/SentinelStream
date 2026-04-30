from decimal import Decimal

from app.services.ml_scorer import MLScorer
from app.schemas import TransactionCreate


class DummyUser:
    home_country = "US"
    current_balance = Decimal("100.00")


def test_fallback_ml_score_bounds():
    payload = TransactionCreate(
        user_id="user-1",
        merchant_id="merchant-1",
        amount=Decimal("7000.00"),
        currency="USD",
        country="GB",
    )

    score = MLScorer._fallback_score(payload, DummyUser())
    assert 0.0 <= score <= 1.0
    assert score >= 0.8

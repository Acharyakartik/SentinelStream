from app.services.idempotency import build_request_hash


def test_request_hash_is_stable_for_same_payload_order():
    payload_a = {"amount": "10.00", "user_id": "u1", "country": "US"}
    payload_b = {"country": "US", "user_id": "u1", "amount": "10.00"}

    assert build_request_hash(payload_a) == build_request_hash(payload_b)

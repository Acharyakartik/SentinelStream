# Software Requirements Specification (SRS)

## 1. Purpose
SentinelStream provides a low-latency fraud-interception service between payment gateway and internal ledger for a high-scale neo-bank.

## 2. Functional Requirements
- FR-1: Accept card transaction authorization requests via REST API.
- FR-2: Validate payload strictly with Pydantic models.
- FR-3: Enforce idempotency using client-provided `Idempotency-Key`.
- FR-4: Execute dynamic fraud rules from database configuration.
- FR-5: Execute ML anomaly score using pre-trained Isolation Forest pipeline.
- FR-6: Combine rule and ML scores into final risk score `[0.0, 1.0]`.
- FR-7: Approve or decline transaction based on policy threshold.
- FR-8: Persist immutable ledger record for every processed transaction.
- FR-9: Expose current balance and transaction history APIs.
- FR-10: Emit async webhook notifications for merchant systems.

## 3. Non-Functional Requirements
- NFR-1: Throughput target: tens of thousands TPS in production scale-out.
- NFR-2: Local benchmark target: >=100 req/s.
- NFR-3: p95 end-to-end processing target: <200ms.
- NFR-4: Zero double-charge for retried requests with same key.
- NFR-5: Secure endpoints with JWT bearer tokens.
- NFR-6: Code coverage target: >=80%.

## 4. API Contract Stability
- OpenAPI generated from FastAPI; all payloads typed via Pydantic.
- Versioned prefix `/v1`.

## 5. Data Model (3NF-Oriented)
- `user_profiles`: user attributes and current balance.
- `transactions`: immutable transaction ledger facts.
- `idempotency_records`: replay-safe request-response mapping.
- `fraud_rules`: configurable, runtime-evaluated rule expressions.

## 6. Security Requirements
- JWT token required for transaction and user data endpoints.
- SQLAlchemy parameterized queries mitigate injection risk.
- Idempotency key conflict handling prevents replay misuse.

## 7. Observability
- Request timing header `X-Process-Time-Ms`.
- Celery retry policy for webhook delivery resilience.

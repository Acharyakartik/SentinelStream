# Architecture Overview

## Runtime Components
- Payment Gateway -> SentinelStream API (FastAPI)
- Fraud pipeline (Rule Engine + MLScorer)
- Immutable ledger write (PostgreSQL)
- Burst control and limiter state (Redis)
- Async notification fan-out (Celery + RabbitMQ)
- Reverse proxy and TLS termination (Nginx)

## Transaction Decision Policy
- Final risk score = `0.65 * ml_score + 0.35 * rule_score`
- Decline threshold = `0.70`

## Failure Recovery Strategy
- Webhook dispatch decoupled from request-response path.
- Celery retries with exponential backoff.
- API response does not block on external webhook recipient availability.

## Data Flow
1. Validate request payload.
2. Enforce idempotency key uniqueness + payload hash integrity.
3. Evaluate rules from DB.
4. Evaluate model score from serialized pipeline.
5. Persist immutable transaction and update balance if approved.
6. Return decision response.
7. Trigger async webhook task.

# SentinelStream - High-Throughput Transaction Guard

SentinelStream is a FastAPI-based fraud detection gateway designed for real-time payment authorization with layered rule + ML scoring under strict latency constraints.

## Core Capabilities
- Real-time fraud scoring pipeline (`<200ms` target)
- Idempotency protection to prevent duplicate charging
- Immutable transaction ledger in PostgreSQL
- User balance and transaction history APIs
- Dynamic database-driven fraud rules
- Async webhook dispatch via Celery/RabbitMQ
- Redis-backed burst rate limiting (FastAPI-Limiter)

## Architecture
- API: FastAPI + Pydantic
- Database: PostgreSQL (SQLAlchemy AsyncIO)
- Cache/Rate limiting: Redis
- Queue: RabbitMQ + Celery workers
- Fraud intelligence: Rule engine + pre-trained Scikit-Learn Isolation Forest
- Schema migration: Alembic (versioned migrations)

See [docs/SRS.md](docs/SRS.md), [docs/architecture.md](docs/architecture.md), and [docs/sequence-diagram.md](docs/sequence-diagram.md).

## Quick Start
1. Copy `.env.example` to `.env`
2. Start infra:
   - `docker compose up -d postgres redis rabbitmq`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run API:
   - `uvicorn app.main:app --reload`
5. Run Celery worker:
   - `celery -A app.workers.celery_app.celery_app worker -Q webhooks --loglevel=info`

## Database Migrations
- Apply migrations: `alembic upgrade head`
- Create migration: `alembic revision --autogenerate -m "message"`

## API
- `POST /v1/auth/token` -> issue JWT
- `POST /v1/transactions` -> create/score transaction
- `GET /v1/users/{user_id}/balance` -> current balance
- `GET /v1/users/{user_id}/transactions` -> transaction history

## Idempotency
`POST /v1/transactions` requires `Idempotency-Key` header.
Repeated requests with the same key and identical payload return the original response.

## Redis Profile Cache
- User profiles are cached with a short TTL (`user_profile:{user_id}`) to reduce repeated DB lookups.
- Balance reads prefer cache first and backfill on cache miss.

## Testing
- `pytest -q`

## Load Testing (Locust target)
- Baseline objective: sustain `>=100 req/s` locally
- Include JWT token reuse and unique idempotency keys in each request
- Run: `locust -f tests/locustfile.py --host http://localhost:8000`

## Readiness Check
- Static readiness: `python scripts/readiness_check.py`
- Full checklist: `docs/readiness.md`

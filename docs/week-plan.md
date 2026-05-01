# Week-by-Week Execution Plan

## Week 1 - Planning & Architecture
- Finalize SRS and architecture constraints.
- Validate schema normalization and initial indexing strategy.
- Lock API contracts and OpenAPI signatures.
- Setup CI pipeline for tests and linting.
- Draft admin dashboard wireframes (outside this repo).

## Week 2 - Core Transaction Pipeline
- Harden POST `/v1/transactions` hot path.
- Add Redis-backed profile caching to reduce DB roundtrips.
- Run Locust load tests and tune AsyncIO pool sizing.
- Validate sustained >=100 req/s on local infra.

## Week 3 - Intelligence Layer
- Train/refresh Isolation Forest pipeline and serialize with joblib.
- Add rule validation UX and non-technical authoring safeguards.
- Expand Celery worker pool for alert delivery.
- Enforce p95 latency budget checks under mixed load.

## Week 4 - Finalization & Deployment
- Containerize all services and add production profiles.
- Configure Nginx TLS + horizontal load routing.
- Complete JWT role/claim authorization model.
- Expand PyTest coverage to >80% and run security audit.

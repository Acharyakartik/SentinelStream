# Readiness Status Guide

Run:

```bash
python scripts/readiness_check.py
```

This verifies:
- project-critical files exist
- Python syntax integrity

This does not verify:
- package installation
- live infra availability
- runtime API behavior
- load/latency target attainment

Full readiness requires:
1. `pip install -r requirements.txt`
2. `alembic upgrade head`
3. `docker compose up -d postgres redis rabbitmq`
4. `pytest -q`
5. `locust -f tests/locustfile.py --host http://localhost:8000`

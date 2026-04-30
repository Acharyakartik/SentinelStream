from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.send_webhook_notification", autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_webhook_notification(merchant_id: str, transaction_id: str, status: str, risk_score: float) -> dict:
    # In production this would POST to a merchant webhook URL.
    return {
        "merchant_id": merchant_id,
        "transaction_id": transaction_id,
        "status": status,
        "risk_score": risk_score,
    }

from celery import Celery

from app.core.config import settings


celery_app = Celery("sentinelstream", broker=settings.rabbitmq_url, backend=settings.redis_url)
celery_app.conf.task_routes = {"app.workers.tasks.send_webhook_notification": {"queue": "webhooks"}}

from celery import Celery

from app.settings import settings

celery_app = Celery(
    "deribit_price_tracker", broker=settings.CELERY_BROKER_URL, include=["app.worker.tasks"]
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_ignore_result=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "fetch-index-prices": {
            "task": "app.worker.tasks.fetch_prices",
            "schedule": float(settings.FETCH_INTERVAL_SECONDS),
            # Если воркер лежал накопившиеся задачи не имеют смысла-цена уже устарела
            "options": {"expires": settings.FETCH_INTERVAL_SECONDS},
        },
    },
)

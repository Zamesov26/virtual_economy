from celery import Celery
from celery.schedules import crontab

from app.background.settings import CelerySettings

settings = CelerySettings()

celery_app = Celery(
    "app",
    broker=settings.broker_url,
    backend=settings.backend_url,
)

celery_app.conf.timezone = settings.timezone
celery_app.conf.enable_utc = settings.enable_utc

celery_app.autodiscover_tasks(["app.background.tasks"])

celery_app.conf.beat_schedule = {
    "clear-inventory-cache-daily": {
        "task": "app.background.tasks.clear_inventory_cache.clear_inventory_cache",
        "schedule": crontab(hour=3, minute=0),
    }
}

from celery import Celery
from celery.schedules import crontab
import os
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from app.integrations.queue.dlq_handlers import register_task_failure_handlers

from app.core.config import settings


if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        integrations=[CeleryIntegration(monitor_beat_tasks=True)],
    )


celery_app = Celery(
    "ecommerce_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    # Reliability-focused delivery semantics.
    task_acks_late=True,
    task_acks_on_failure_or_timeout=False,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=None,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    broker_transport_options={
        "visibility_timeout": 3600,
        "retry_on_timeout": True,
    },
    result_backend_transport_options={
        "visibility_timeout": 3600,
        "retry_policy": {
            "timeout": 5.0,
        },
    },
    task_default_queue="default",
    task_create_missing_queues=True,
    task_routes={
        "send_welcome_email": {"queue": "email"},
        "send_order_confirmation_email": {"queue": "email"},
        "notify_admin_new_order": {"queue": "email"},
        "send_shipping_update_email": {"queue": "email"},
        "cleanup_expired_orders": {"queue": "maintenance"},
        # Dead-letter queue route for permanently failed tasks
        "app.integrations.queue.dlq_handlers.handle_dead_letter_task": {"queue": "dlq"},
    },
    imports=["app.tasks.email_tasks", "app.tasks.order_tasks"],
)

celery_app.conf.beat_schedule = {
    "cancel-unpaid-orders-every-hour": {
        "task": "cleanup_expired_orders",
        "schedule": crontab(minute=0, hour="*"),
    },
}

# Register failure handlers for dead-letter processing and alerting
register_task_failure_handlers(celery_app)

celery = celery_app

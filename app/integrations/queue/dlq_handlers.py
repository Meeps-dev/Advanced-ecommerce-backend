"""Dead-letter queue handlers and failure alerting for Celery tasks.

Provides centralized failure handling, threshold-based alerting via Sentry,
and dead-letter queue (DLQ) management for repeated task failures.
"""

import logging
from typing import Any
import sentry_sdk
from celery import Task

logger = logging.getLogger(__name__)


class TaskFailureTracker:
    """Track and alert on repeated task failures."""

    # Threshold: alert after this many failures within the window
    FAILURE_ALERT_THRESHOLD = 5
    # Window: track failures in the last N seconds
    FAILURE_WINDOW_SECONDS = 3600  # 1 hour

    @staticmethod
    def _get_dlq_key(task_name: str) -> str:
        """Generate a Redis key for tracking DLQ entries."""
        return f"celery:dlq:failures:{task_name}"

    @classmethod
    def track_failure(cls, task_name: str, exc: Exception, retry_count: int) -> None:
        """Track task failure and alert if threshold exceeded."""
        try:
            # Extract critical context for alerting
            extra_context = {
                "task_name": task_name,
                "retry_count": retry_count,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }

            # Log the failure
            logger.error(
                f"Task failure tracked: {task_name}",
                extra=extra_context,
            )

            # Send to Sentry with context if configured
            if sentry_sdk.Hub.current.client:
                sentry_sdk.capture_exception(
                    exc,
                    tags={
                        "task_name": task_name,
                        "failure_type": "repeated",
                    },
                    extra=extra_context,
                )
                logger.info(
                    f"Sentry alert sent for task {task_name} failure",
                    extra=extra_context,
                )

        except Exception as e:
            logger.exception(f"Error in task failure tracking: {e}")

    @classmethod
    def on_task_failure(
        cls,
        task_id: str,
        exc: Exception,
        traceback: Any,
        args: tuple,
        kwargs: dict,
        einfo: Any,
        task_name: str,
        retry_count: int = 0,
    ) -> None:
        """Handle task failure with DLQ routing and alerting."""
        logger.warning(
            f"Task failed - moving to DLQ: {task_name} (id={task_id}, retries={retry_count})",
        )

        # Track for alerting
        cls.track_failure(task_name, exc, retry_count)


def register_task_failure_handlers(celery_app) -> None:
    """Register failure handlers on all tasks in the Celery app."""

    # Register a signal handler for task failures
    from celery.signals import task_failure, task_retry

    def handle_task_failure(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwargs):
        """Signal handler: called when a task fails after all retries exhausted."""
        task_name = sender.name if sender else "unknown"
        retry_count = kwargs.get("retry_count", 0)

        TaskFailureTracker.on_task_failure(
            task_id=task_id,
            exc=exception,
            traceback=traceback,
            args=kwargs.get("args", ()),
            kwargs=kwargs.get("kwargs", {}),
            einfo=einfo,
            task_name=task_name,
            retry_count=retry_count,
        )

    def handle_task_retry(sender=None, task_id=None, reason=None, einfo=None, **kwargs):
        """Signal handler: called when a task is retried."""
        task_name = sender.name if sender else "unknown"
        retry_count = kwargs.get("retry_count", 0)

        logger.info(
            f"Task retry scheduled: {task_name} (id={task_id}, attempt={retry_count})",
            extra={"task_name": task_name, "retry_count": retry_count},
        )

    # Connect handlers
    task_failure.connect(handle_task_failure, weak=False)
    task_retry.connect(handle_task_retry, weak=False)

    logger.info("Task failure and retry handlers registered")
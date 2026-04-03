import logging
from app.modules.analytics.infrastructure.models.overview import AnalyticsOverview
from app.modules.analytics.infrastructure.repository import AnalyticsRepository


logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def get_overview(self) -> AnalyticsOverview:
        """Build the analytics overview DTO from repository aggregates."""
        metrics = self.repo.get_overview_metrics()
        # Structured log fields are consumed by centralized observability pipelines.
        logger.info(
            "analytics_overview_fetched",
            extra={
                "event": "analytics_overview_fetched",
                "entity": "analytics",
            },
        )
        return AnalyticsOverview(**metrics)

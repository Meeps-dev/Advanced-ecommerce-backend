from fastapi import APIRouter, Depends

from app.dependencies.auth import admin_required
from app.dependencies.services import get_analytics_service
from app.modules.analytics.api.schemas import AnalyticsOverviewResponse
from app.modules.analytics.application.service import AnalyticsService


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(
    service: AnalyticsService = Depends(get_analytics_service),
    # Dependency enforces admin access even though the value is not read directly.
    current_admin=Depends(admin_required),
):
    return service.get_overview()

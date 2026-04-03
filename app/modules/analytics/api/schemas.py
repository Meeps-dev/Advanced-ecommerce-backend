from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    total_users: int
    total_orders: int
    paid_orders: int
    pending_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    total_products: int
    low_stock_products: int
    new_users_last_30_days: int
    orders_last_7_days: int
    successful_payments: int
    failed_payments: int

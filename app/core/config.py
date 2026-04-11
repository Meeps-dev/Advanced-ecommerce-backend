from pydantic_settings import BaseSettings, SettingsConfigDict, Field

class Settings(BaseSettings):
    # These match the keys in your .env
    database_url: str = Field(validation_alias="DATABASE_URL") 
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Rate Limiting
    login_rate_limit_max_attempts: int = 5
    login_rate_limit_window_minutes: int = 15

    # Infrastructure
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
        # Task Failure Alerting
    task_failure_alert_threshold: int = 5  # Alert after N failures
    task_failure_window_seconds: int = 3600  # Within this time window
    enable_dlq_alerts: bool = True  # Enable Sentry alerts via DLQ

    # Email
    mail_from: str
    mail_from_name: str = "Meeps Store"
    admin_email: str | None = None
    resend_api_key: str
    

    # Payment Gateway (Mock)
    
    paystack_secret_key: str
    paystack_initialize_url: str = "https://api.paystack.co/transaction/initialize"
    paystack_callback_url: str = "http://localhost:3000/payment-success"
    password_reset_frontend_url: str = "http://localhost:3000/reset-password"


    # Sentry
    sentry_dsn: str | None = None
    sentry_traces_sample_rate: float = 1.0
    sentry_profiles_sample_rate: float = 1.0
    sentry_environment: str = "development"


    # This is the "Magic" that connects to your .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",      # Ignores extra variables in .env
        case_sensitive=False, # Allows DATABASE_URL to match database_url
        
    )


settings = Settings()

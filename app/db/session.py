from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Production-grade connection pooling for ecommerce backend
engine = create_engine(
    settings.database_url,
    echo=True,
    poolclass=QueuePool,
    pool_size=10,                      # Base: 10 open connections
    max_overflow=20,                   # Burst: allow +20 temporary connections
    pool_recycle=3600,                 # Recycle after 1hr (cloud DB timeouts)
    pool_pre_ping=True,                # Test each connection before use (no "connection lost" errors)
    connect_args={"connect_timeout": 10},
    echo_pool=False,
)

# Optional: Log pool status for monitoring
@event.listens_for(engine.pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    logger.debug(
        "db_connection_checked_out",
        extra={
            "event": "db_connection_checked_out",
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),
        },
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
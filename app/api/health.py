from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.dependencies.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/db")
def check_db_health(db: Session = Depends(get_db)):
    """Check database connection pool health."""
    try:
        # Simple query to test connection
        db.execute(text("SELECT 1"))
        
        # Get pool stats
        pool = db.get_bind().pool
        return {
            "status": "healthy",
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total": pool.size() + pool.overflow(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }

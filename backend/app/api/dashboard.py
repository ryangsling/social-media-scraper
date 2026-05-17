from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.scrape_job import ScrapeJob, ScrapeResult, StatusEnum
from app.schemas.schemas import DashboardStats

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    base = db.query(ScrapeJob).filter(ScrapeJob.user_id == current_user.id)
    total = base.count()
    completed = base.filter(ScrapeJob.status == StatusEnum.completed).count()
    failed = base.filter(ScrapeJob.status == StatusEnum.failed).count()
    pending = base.filter(ScrapeJob.status.in_([StatusEnum.pending, StatusEnum.running])).count()

    total_results = db.query(func.sum(ScrapeJob.result_count)).filter(
        ScrapeJob.user_id == current_user.id
    ).scalar() or 0

    platforms = db.query(ScrapeJob.platform).filter(
        ScrapeJob.user_id == current_user.id
    ).distinct().all()
    platforms_used = [p[0].value if hasattr(p[0], 'value') else str(p[0]) for p in platforms]

    recent_jobs = base.order_by(ScrapeJob.created_at.desc()).limit(10).all()

    return DashboardStats(
        total_jobs=total,
        completed_jobs=completed,
        failed_jobs=failed,
        pending_jobs=pending,
        total_results=int(total_results),
        platforms_used=platforms_used,
        recent_jobs=recent_jobs,
    )

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.scrape_job import ScrapeJob, ScrapeResult, StatusEnum
from app.models.user import User
from app.schemas.schemas import (
    ScrapeJobDetail,
    ScrapeJobOut,
    ScrapeRequest,
    ScrapeResultOut,
)
from app.tasks.scrape_tasks import scrape_social_media

router = APIRouter()


@router.post("/start", response_model=ScrapeJobOut)
def start_scrape(
    req: ScrapeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = ScrapeJob(
        user_id=current_user.id,
        platform=req.platform,
        job_type=req.job_type,
        target=req.target,
        method="apify" if req.use_apify else "free",
        status=StatusEnum.pending,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Dispatch Celery task
    task = scrape_social_media.delay(
        job_id=job.id,
        platform=req.platform.value,
        job_type=req.job_type.value,
        target=req.target,
        use_apify=req.use_apify,
        max_results=req.max_results,
    )
    job.celery_task_id = task.id
    db.commit()
    db.refresh(job)
    return job


@router.get("/jobs", response_model=List[ScrapeJobOut])
def list_jobs(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ScrapeJob).filter(ScrapeJob.user_id == current_user.id)
    if platform:
        q = q.filter(ScrapeJob.platform == platform)
    if status:
        q = q.filter(ScrapeJob.status == status)
    return q.order_by(ScrapeJob.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/jobs/{job_id}", response_model=ScrapeJobDetail)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = (
        db.query(ScrapeJob)
        .filter(ScrapeJob.id == job_id, ScrapeJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = (
        db.query(ScrapeJob)
        .filter(ScrapeJob.id == job_id, ScrapeJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}


@router.get("/jobs/{job_id}/results", response_model=List[ScrapeResultOut])
def get_results(
    job_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = (
        db.query(ScrapeJob)
        .filter(ScrapeJob.id == job_id, ScrapeJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    results = (
        db.query(ScrapeResult)
        .filter(ScrapeResult.job_id == job_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return results


@router.get("/platforms")
def get_platforms():
    return {
        "platforms": [
            {
                "id": "twitter",
                "name": "Twitter / X",
                "free": True,
                "paid": True,
                "icon": "🐦",
            },
            {
                "id": "instagram",
                "name": "Instagram",
                "free": True,
                "paid": True,
                "icon": "📸",
            },
            {
                "id": "linkedin",
                "name": "LinkedIn",
                "free": False,
                "paid": True,
                "icon": "💼",
            },
            {
                "id": "facebook",
                "name": "Facebook",
                "free": False,
                "paid": True,
                "icon": "👤",
            },
            {
                "id": "reddit",
                "name": "Reddit",
                "free": True,
                "paid": False,
                "icon": "🤖",
            },
            {
                "id": "youtube",
                "name": "YouTube",
                "free": True,
                "paid": False,
                "icon": "▶️",
            },
            {
                "id": "tiktok",
                "name": "TikTok",
                "free": False,
                "paid": True,
                "icon": "🎵",
            },
            {
                "id": "quora",
                "name": "Quora",
                "free": False,
                "paid": False,
                "icon": "❓",
            },
        ]
    }

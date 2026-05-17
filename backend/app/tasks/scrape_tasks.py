import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from datetime import datetime

from celery import Task

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.scrape_job import ScrapeJob, ScrapeResult, StatusEnum

logger = logging.getLogger(__name__)


def _save_results(db, job_id: int, raw_results: list):
    count = 0
    for r in raw_results:
        if "error" in r:
            continue
        try:
            pub = r.get("published_at")
            if isinstance(pub, str):
                try:
                    pub = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                except Exception:
                    pub = None
            result = ScrapeResult(
                job_id=job_id,
                platform=r.get("platform", ""),
                content_type=r.get("content_type", "post"),
                post_id=r.get("post_id"),
                author=r.get("author"),
                author_url=r.get("author_url"),
                content=r.get("content"),
                url=r.get("url"),
                likes=int(r.get("likes") or 0),
                comments=int(r.get("comments") or 0),
                shares=int(r.get("shares") or 0),
                views=int(r.get("views") or 0),
                published_at=pub,
                raw_data=r.get("raw_data"),
            )
            db.add(result)
            count += 1
        except Exception as e:
            logger.error(f"Error saving result: {e}")
    db.commit()
    return count


def _run_with_timeout(fn, target: str, max_results: int):
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(fn, target, max_results)
        try:
            return future.result(timeout=settings.SCRAPER_TIMEOUT_SECONDS)
        except FutureTimeoutError:
            return [
                {
                    "error": (
                        f"Scraper timed out after {settings.SCRAPER_TIMEOUT_SECONDS} seconds. "
                        "Try a smaller target or switch method."
                    )
                }
            ]
        except Exception as e:
            return [{"error": str(e)}]


@celery_app.task(bind=True, name="scrape_social_media", max_retries=2)
def scrape_social_media(
    self: Task,
    job_id: int,
    platform: str,
    job_type: str,
    target: str,
    use_apify: bool,
    max_results: int,
):
    db = SessionLocal()
    try:
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        if not job:
            return {"error": "Job not found"}

        job.status = StatusEnum.running
        job.celery_task_id = self.request.id
        db.commit()

        raw_results = []

        if use_apify:
            if not settings.APIFY_API_TOKEN:
                raw_results = [
                    {
                        "error": "APIFY_API_TOKEN not set. Add it to your .env file.",
                        "platform": platform,
                    }
                ]
            else:
                from app.services.apify_scraper import (
                    scrape_facebook_apify,
                    scrape_instagram_apify,
                    scrape_linkedin_apify,
                    scrape_tiktok_apify,
                    scrape_twitter_apify,
                    scrape_twitter_apify_search,
                )

                dispatch = {
                    "instagram": scrape_instagram_apify,
                    "linkedin": scrape_linkedin_apify,
                    "facebook": scrape_facebook_apify,
                    "tiktok": scrape_tiktok_apify,
                }
                if platform == "twitter":
                    if job_type in ("keyword", "hashtag"):
                        raw_results = _run_with_timeout(
                            scrape_twitter_apify_search, target, max_results
                        )
                    else:
                        raw_results = _run_with_timeout(
                            scrape_twitter_apify, target, max_results
                        )
                else:
                    fn = dispatch.get(platform)
                    if fn:
                        raw_results = _run_with_timeout(fn, target, max_results)
                    else:
                        raw_results = [
                            {"error": f"Apify scraper not available for {platform}"}
                        ]
        else:
            from app.services.free_scraper import (
                scrape_instagram_free,
                scrape_reddit_free,
                scrape_twitter_free,
                scrape_youtube_free,
            )

            dispatch = {
                "twitter": lambda t, n: scrape_twitter_free(t, n),
                "instagram": lambda t, n: scrape_instagram_free(t, n),
                "reddit": lambda t, n: scrape_reddit_free(t, job_type, n),
                "youtube": lambda t, n: scrape_youtube_free(t, n),
            }
            fn = dispatch.get(platform)
            if fn:
                raw_results = _run_with_timeout(fn, target, max_results)
            else:
                raw_results = [
                    {"error": f"Free scraper not available for {platform}. Use Apify."}
                ]

        if not raw_results:
            job.status = StatusEnum.failed
            job.error_message = "No results returned by scraper."
        else:
            errors = [r for r in raw_results if "error" in r]
            if errors and len(errors) == len(raw_results):
                job.status = StatusEnum.failed
                job.error_message = errors[0].get("error", "Unknown error")
            else:
                count = _save_results(db, job_id, raw_results)
                if count == 0:
                    job.status = StatusEnum.failed
                    job.error_message = "No valid results returned by scraper."
                else:
                    job.status = StatusEnum.completed
                    job.result_count = count
                    job.completed_at = datetime.utcnow()

        db.commit()
        return {"job_id": job_id, "status": job.status, "count": job.result_count}

    except Exception as e:
        logger.error(f"Task failed for job {job_id}: {e}")
        try:
            job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
            if job:
                job.status = StatusEnum.failed
                job.error_message = str(e)
                db.commit()
        except Exception:
            pass
        raise self.retry(exc=e, countdown=30)
    finally:
        db.close()

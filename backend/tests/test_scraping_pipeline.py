from app.models.scrape_job import ScrapeJob, ScrapeResult, StatusEnum
from app.tasks import scrape_tasks
import time


def _register_and_login(client, email, username):
    register_response = client.post(
        "/api/auth/register",
        json={"email": email, "username": username, "password": "supersecret"},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "supersecret"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, register_response.json()


def test_start_scrape_creates_pending_job_and_sets_task_id(client):
    headers, _ = _register_and_login(client, "start@example.com", "starter")

    class DummyTask:
        id = "task-123"

    original_delay = scrape_tasks.scrape_social_media.delay
    scrape_tasks.scrape_social_media.delay = lambda **kwargs: DummyTask()
    try:
        payload = {
            "platform": "twitter",
            "job_type": "profile",
            "target": "openai",
            "use_apify": False,
            "max_results": 20,
        }
        response = client.post("/api/scraping/start", json=payload, headers=headers)
    finally:
        scrape_tasks.scrape_social_media.delay = original_delay

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["method"] == "free"

    job_detail = client.get(f"/api/scraping/jobs/{data['id']}", headers=headers)
    assert job_detail.status_code == 200
    assert job_detail.json()["status"] == "pending"


def test_task_pipeline_running_to_completed_and_result_normalization(db_session_factory, monkeypatch):
    db = db_session_factory()
    try:
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.models.scrape_job import PlatformEnum, ScrapeJobTypeEnum

        user = User(
            email="pipeline@example.com",
            username="pipeline",
            hashed_password=get_password_hash("supersecret"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        job = ScrapeJob(
            user_id=user.id,
            platform=PlatformEnum.twitter,
            job_type=ScrapeJobTypeEnum.profile,
            target="target",
            method="free",
            status=StatusEnum.pending,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = job.id
    finally:
        db.close()

    monkeypatch.setattr(scrape_tasks, "SessionLocal", db_session_factory)

    original_save_results = scrape_tasks._save_results

    def wrapped_save_results(db_obj, job_id_arg, raw_results):
        running_job = db_obj.query(ScrapeJob).filter(ScrapeJob.id == job_id_arg).first()
        assert running_job.status == StatusEnum.running
        return original_save_results(db_obj, job_id_arg, raw_results)

    monkeypatch.setattr(scrape_tasks, "_save_results", wrapped_save_results)
    monkeypatch.setattr(
        "app.services.free_scraper.scrape_twitter_free",
        lambda target, max_results: [
            {
                "platform": "twitter",
                "content_type": "post",
                "post_id": "abc",
                "author": "tester",
                "content": "hello",
                "url": "https://twitter.com/x/status/1",
                "likes": "10",
                "comments": "2",
                "shares": "1",
                "views": "99",
                "published_at": None,
                "raw_data": {"k": "v"},
            },
            {"error": "skip me", "platform": "twitter"},
        ],
    )

    result = scrape_tasks.scrape_social_media.run(
        job_id=job_id,
        platform="twitter",
        job_type="profile",
        target="target",
        use_apify=False,
        max_results=20,
    )
    assert result["job_id"] == job_id

    verify_db = db_session_factory()
    try:
        job = verify_db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        rows = verify_db.query(ScrapeResult).filter(ScrapeResult.job_id == job_id).all()

        assert job.status == StatusEnum.completed
        assert job.result_count == 1
        assert len(rows) == 1
        assert rows[0].likes == 10
        assert rows[0].comments == 2
        assert rows[0].shares == 1
        assert rows[0].views == 99
    finally:
        verify_db.close()


def test_task_pipeline_marks_failed_when_all_results_are_errors(db_session_factory, monkeypatch):
    db = db_session_factory()
    try:
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.models.scrape_job import PlatformEnum, ScrapeJobTypeEnum

        user = User(
            email="fail@example.com",
            username="failuser",
            hashed_password=get_password_hash("supersecret"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        job = ScrapeJob(
            user_id=user.id,
            platform=PlatformEnum.twitter,
            job_type=ScrapeJobTypeEnum.profile,
            target="target",
            method="free",
            status=StatusEnum.pending,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = job.id
    finally:
        db.close()

    monkeypatch.setattr(scrape_tasks, "SessionLocal", db_session_factory)
    monkeypatch.setattr(
        "app.services.free_scraper.scrape_twitter_free",
        lambda target, max_results: [{"error": "forced failure", "platform": "twitter"}],
    )

    scrape_tasks.scrape_social_media.run(
        job_id=job_id,
        platform="twitter",
        job_type="profile",
        target="target",
        use_apify=False,
        max_results=20,
    )

    verify_db = db_session_factory()
    try:
        job = verify_db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        rows = verify_db.query(ScrapeResult).filter(ScrapeResult.job_id == job_id).all()

        assert job.status == StatusEnum.failed
        assert job.error_message == "forced failure"
        assert len(rows) == 0
    finally:
        verify_db.close()


def test_run_with_timeout_returns_error_for_slow_scraper(monkeypatch):
    monkeypatch.setattr(scrape_tasks.settings, "SCRAPER_TIMEOUT_SECONDS", 1)

    def slow_scraper(target, max_results):
        time.sleep(2)
        return []

    out = scrape_tasks._run_with_timeout(slow_scraper, "target", 10)
    assert len(out) == 1
    assert "error" in out[0]
    assert "timed out" in out[0]["error"]


def test_run_with_timeout_returns_error_for_exception():
    def broken_scraper(target, max_results):
        raise RuntimeError("actor failed")

    out = scrape_tasks._run_with_timeout(broken_scraper, "target", 10)
    assert len(out) == 1
    assert out[0]["error"] == "actor failed"

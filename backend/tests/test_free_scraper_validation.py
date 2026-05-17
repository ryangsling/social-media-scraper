import types

from app.services import free_scraper
from app.tasks import scrape_tasks
from app.models.scrape_job import ScrapeJob, StatusEnum


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
    return {"Authorization": f"Bearer {token}"}


def test_platforms_endpoint_disables_linkedin_free(client):
    headers = _register_and_login(client, "platforms@example.com", "platforms")
    response = client.get("/api/scraping/platforms", headers=headers)
    assert response.status_code == 200
    platforms = {p["id"]: p for p in response.json()["platforms"]}
    assert platforms["linkedin"]["free"] is False
    assert platforms["quora"]["free"] is False
    assert platforms["quora"]["paid"] is False


def test_twitter_free_returns_clear_error_when_nitter_unavailable(monkeypatch):
    monkeypatch.setattr(free_scraper, "NITTER_INSTANCES", ["https://nitter.invalid"])

    def fail_get(*args, **kwargs):
        raise RuntimeError("connection failed")

    monkeypatch.setattr(free_scraper.httpx, "get", fail_get)
    results = free_scraper.scrape_twitter_free("openai", max_results=5)

    assert len(results) == 1
    assert "error" in results[0]
    assert "Nitter" in results[0]["error"]


def test_reddit_free_requires_credentials(monkeypatch):
    monkeypatch.setattr(free_scraper.settings, "REDDIT_CLIENT_ID", None)
    monkeypatch.setattr(free_scraper.settings, "REDDIT_CLIENT_SECRET", None)

    results = free_scraper.scrape_reddit_free("python", job_type="keyword", max_results=5)

    assert len(results) == 1
    assert "error" in results[0]
    assert "REDDIT_CLIENT_ID" in results[0]["error"]


def test_youtube_free_surfaces_ytdlp_error(monkeypatch):
    fake_proc = types.SimpleNamespace(returncode=1, stdout="", stderr="network blocked")

    def fake_run(*args, **kwargs):
        return fake_proc

    monkeypatch.setattr("subprocess.run", fake_run)
    results = free_scraper.scrape_youtube_free("openai", max_results=5)

    assert len(results) == 1
    assert "error" in results[0]
    assert "yt-dlp" in results[0]["error"]


def test_task_fails_for_linkedin_free_mode(db_session_factory, monkeypatch):
    db = db_session_factory()
    try:
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.models.scrape_job import PlatformEnum, ScrapeJobTypeEnum

        user = User(
            email="linkedinfree@example.com",
            username="linkedinfree",
            hashed_password=get_password_hash("supersecret"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        job = ScrapeJob(
            user_id=user.id,
            platform=PlatformEnum.linkedin,
            job_type=ScrapeJobTypeEnum.profile,
            target="some-user",
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

    scrape_tasks.scrape_social_media.run(
        job_id=job_id,
        platform="linkedin",
        job_type="profile",
        target="some-user",
        use_apify=False,
        max_results=5,
    )

    verify_db = db_session_factory()
    try:
        job = verify_db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        assert job.status == StatusEnum.failed
        assert "Free scraper not available for linkedin" in job.error_message
    finally:
        verify_db.close()

from app.models.scrape_job import PlatformEnum, ScrapeJob, ScrapeJobTypeEnum, ScrapeResult, StatusEnum


def _create_user(client, email, username):
    response = client.post(
        "/api/auth/register",
        json={"email": email, "username": username, "password": "supersecret"},
    )
    assert response.status_code == 200
    return response.json()


def _login_headers(client, email):
    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "supersecret"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_cannot_access_another_users_job(client, db_session_factory):
    user1 = _create_user(client, "u1@example.com", "user1")
    user2 = _create_user(client, "u2@example.com", "user2")

    db = db_session_factory()
    try:
        protected_job = ScrapeJob(
            user_id=user1["id"],
            platform=PlatformEnum.twitter,
            job_type=ScrapeJobTypeEnum.profile,
            target="target_u1",
            method="free",
            status=StatusEnum.completed,
        )
        db.add(protected_job)
        db.commit()
        db.refresh(protected_job)
        protected_job_id = protected_job.id
    finally:
        db.close()

    headers_user2 = _login_headers(client, "u2@example.com")

    get_response = client.get(f"/api/scraping/jobs/{protected_job_id}", headers=headers_user2)
    assert get_response.status_code == 404

    delete_response = client.delete(f"/api/scraping/jobs/{protected_job_id}", headers=headers_user2)
    assert delete_response.status_code == 404

    headers_user1 = _login_headers(client, "u1@example.com")
    own_get_response = client.get(f"/api/scraping/jobs/{protected_job_id}", headers=headers_user1)
    assert own_get_response.status_code == 200


def test_delete_job_removes_results_cascade(client, db_session_factory):
    user = _create_user(client, "owner@example.com", "owner")

    db = db_session_factory()
    try:
        job = ScrapeJob(
            user_id=user["id"],
            platform=PlatformEnum.reddit,
            job_type=ScrapeJobTypeEnum.keyword,
            target="growth",
            method="free",
            status=StatusEnum.completed,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        result = ScrapeResult(
            job_id=job.id,
            platform="reddit",
            content_type="post",
            content="test content",
            likes=1,
            comments=2,
            shares=3,
            views=4,
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        job_id = job.id
        result_id = result.id
    finally:
        db.close()

    headers = _login_headers(client, "owner@example.com")
    delete_response = client.delete(f"/api/scraping/jobs/{job_id}", headers=headers)
    assert delete_response.status_code == 200

    db_verify = db_session_factory()
    try:
        job_exists = db_verify.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        result_exists = db_verify.query(ScrapeResult).filter(ScrapeResult.id == result_id).first()
        assert job_exists is None
        assert result_exists is None
    finally:
        db_verify.close()

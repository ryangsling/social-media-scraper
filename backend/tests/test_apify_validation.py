from app.services import apify_scraper
from app.tasks import scrape_tasks
from app.models.scrape_job import ScrapeJob, StatusEnum


class _FakeDataset:
    def __init__(self, items):
        self._items = items

    def iterate_items(self):
        for item in self._items:
            yield item


class _FakeActor:
    def __init__(self, run):
        self._run = run

    def call(self, run_input):
        return self._run


class _FakeApifyClient:
    def __init__(self, actors, dataset_items):
        self.actors = actors
        self.dataset_items = dataset_items
        self.called_actors = []

    def actor(self, actor_id):
        self.called_actors.append(actor_id)
        run = self.actors[actor_id]
        return _FakeActor(run)

    def dataset(self, dataset_id):
        return _FakeDataset(self.dataset_items.get(dataset_id, []))


def test_apify_scrapers_map_to_expected_actors_and_normalize(monkeypatch):
    actors = {
        "apidojo/tweet-scraper": {"defaultDatasetId": "ds_twitter"},
        "apify/instagram-scraper": {"defaultDatasetId": "ds_instagram"},
        "curious_coder/linkedin-profile-scraper": {"defaultDatasetId": "ds_linkedin"},
        "apify/facebook-posts-scraper": {"defaultDatasetId": "ds_facebook"},
        "clockworks/tiktok-scraper": {"defaultDatasetId": "ds_tiktok"},
    }
    datasets = {
        "ds_twitter": [{"id": "1", "text": "tweet", "author": {"userName": "u"}, "url": "x", "likeCount": 1, "replyCount": 2, "retweetCount": 3, "viewCount": 4}],
        "ds_instagram": [{"shortCode": "abc", "ownerUsername": "u", "caption": "cap", "url": "i", "likesCount": 5, "commentsCount": 6}],
        "ds_linkedin": [{"fullName": "name", "summary": "sum"}],
        "ds_facebook": [{"postId": "p", "pageName": "pg", "text": "fb", "url": "f", "likes": 7, "comments": 8, "shares": 9}],
        "ds_tiktok": [{"id": "t", "authorMeta": {"name": "tk"}, "text": "tt", "webVideoUrl": "tturl", "diggCount": 10, "commentCount": 11, "shareCount": 12, "playCount": 13}],
    }
    fake_client = _FakeApifyClient(actors, datasets)
    monkeypatch.setattr(apify_scraper, "_get_client", lambda: fake_client)

    tw = apify_scraper.scrape_twitter_apify("openai", 1)
    ig = apify_scraper.scrape_instagram_apify("openai", 1)
    li = apify_scraper.scrape_linkedin_apify("openai", 1)
    fb = apify_scraper.scrape_facebook_apify("openai", 1)
    tk = apify_scraper.scrape_tiktok_apify("openai", 1)

    assert tw[0]["platform"] == "twitter"
    assert ig[0]["platform"] == "instagram"
    assert li[0]["platform"] == "linkedin"
    assert fb[0]["platform"] == "facebook"
    assert tk[0]["platform"] == "tiktok"
    assert set(fake_client.called_actors) == set(actors.keys())


def test_task_marks_failed_when_apify_token_missing(db_session_factory, monkeypatch):
    db = db_session_factory()
    try:
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.models.scrape_job import PlatformEnum, ScrapeJobTypeEnum

        user = User(
            email="apify-missing@example.com",
            username="apifymissing",
            hashed_password=get_password_hash("supersecret"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        job = ScrapeJob(
            user_id=user.id,
            platform=PlatformEnum.twitter,
            job_type=ScrapeJobTypeEnum.profile,
            target="openai",
            method="apify",
            status=StatusEnum.pending,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = job.id
    finally:
        db.close()

    monkeypatch.setattr(scrape_tasks, "SessionLocal", db_session_factory)
    monkeypatch.setattr(scrape_tasks.settings, "APIFY_API_TOKEN", "")

    scrape_tasks.scrape_social_media.run(
        job_id=job_id,
        platform="twitter",
        job_type="profile",
        target="openai",
        use_apify=True,
        max_results=5,
    )

    verify_db = db_session_factory()
    try:
        job = verify_db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        assert job.status == StatusEnum.failed
        assert "APIFY_API_TOKEN not set" in job.error_message
    finally:
        verify_db.close()


def test_task_marks_failed_on_empty_apify_dataset(db_session_factory, monkeypatch):
    db = db_session_factory()
    try:
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.models.scrape_job import PlatformEnum, ScrapeJobTypeEnum

        user = User(
            email="apify-empty@example.com",
            username="apifyempty",
            hashed_password=get_password_hash("supersecret"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        job = ScrapeJob(
            user_id=user.id,
            platform=PlatformEnum.twitter,
            job_type=ScrapeJobTypeEnum.profile,
            target="openai",
            method="apify",
            status=StatusEnum.pending,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = job.id
    finally:
        db.close()

    monkeypatch.setattr(scrape_tasks, "SessionLocal", db_session_factory)
    monkeypatch.setattr(scrape_tasks.settings, "APIFY_API_TOKEN", "token")
    monkeypatch.setattr("app.services.apify_scraper.scrape_twitter_apify", lambda target, max_results: [])

    scrape_tasks.scrape_social_media.run(
        job_id=job_id,
        platform="twitter",
        job_type="profile",
        target="openai",
        use_apify=True,
        max_results=5,
    )

    verify_db = db_session_factory()
    try:
        job = verify_db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        assert job.status == StatusEnum.failed
        assert "No results returned by scraper." == job.error_message
    finally:
        verify_db.close()

# Social Scraper Build Plan

## What I Understand

The requested product is a Docker-based web application for scraping social media posts/profiles from platforms such as Twitter/X, Facebook, LinkedIn, Instagram, and other professional or creator-focused platforms.

The app should have a secure login system and a dashboard where the user can:

- See overall scraping stats.
- Review previous scraping history.
- Start a new scrape for a profile, hashtag, keyword, or post-related target.
- Choose between free fallback scraping and paid scraping.
- Open job details and inspect scraped results with engagement metrics.

The project should start with free/trial-friendly approaches where possible, but also support a paid option for reliability. The current strategic default is:

- Free fallback: Nitter, instaloader, PRAW, yt-dlp.
- Paid option: Apify, because it covers several platforms from one provider and is simpler than maintaining separate paid APIs for each network.

The user wants to review this plan before implementation proceeds.

## Current Codebase Baseline

The project already contains a split full-stack structure:

- Backend: FastAPI + Python in `backend/`.
- Frontend: React + Tailwind in `frontend/`.
- Database: PostgreSQL via Docker Compose.
- Queue: Redis + Celery worker.
- Monitoring: Flower on port `5555`.
- Frontend serving: Nginx on port `3000`.

Existing backend capabilities:

- JWT auth routes for register, login, and current user.
- Scraping routes for start, list, detail, delete, results, and platforms.
- Dashboard stats route.
- SQLAlchemy models for users, scrape jobs, and scrape results.
- Celery task for async scraping.
- Free scraper service for Twitter/X, Instagram, Reddit, LinkedIn limited mode, and YouTube.
- Apify service for Twitter/X, Instagram, LinkedIn, Facebook, and TikTok.

Existing frontend capabilities:

- Login and registration.
- Protected dashboard layout.
- Stats cards, platform usage chart, and recent jobs.
- New scrape form with platform picker, job type, free/paid toggle, and max results.
- History table with search, filters, and delete action.
- Job detail page with auto-refresh and result engagement display.

## API And Cost Strategy

Free-first options:

- Twitter/X: Nitter fallback. No API key, but reliability depends on public Nitter instance availability.
- Instagram: instaloader. Useful for public profiles, but rate-limited and fragile.
- Reddit: PRAW using Reddit API credentials. Best free official API option in this app.
- YouTube: yt-dlp. Good for public video metadata without API key.
- LinkedIn: public scraping is limited and fragile.

Paid/reliable options:

- Apify: preferred paid aggregator for Twitter/X, Instagram, LinkedIn, Facebook, TikTok.
- Twitter API v2 Basic can be expensive for simple scraping needs.
- Proxycurl may be useful for LinkedIn profiles, but it is a separate provider and should only be added if Apify is insufficient.
- Meta/Facebook direct APIs are not a good first choice for general public post scraping because access is strict and app review is heavy.

Recommendation:

- Keep free fallback for trial and low-cost testing.
- Use Apify as the first paid production path.
- After testing real workloads, document actual cost per scrape and failure rates before committing to one provider long-term.

## Part 1: Documentation And Plan Review

Goal: Replace stale project-management documentation with accurate scraper-app documentation and get approval before feature implementation.

Checklist:

- [x] Rewrite root `AGENTS.md` for this codebase.
- [x] Rewrite `docs/PLAN.md` for this project.
- [x] User reviews and approves this plan.
- [x] After approval, choose the first implementation part to execute.

Success criteria:

- Docs no longer mention the old Kanban/AI project.
- Plan reflects the current FastAPI, React, PostgreSQL, Redis, Celery, Flower, Docker architecture.
- Plan clearly captures free fallback plus paid scraping strategy.

Tests:

- Documentation-only change. No application tests required for this part.

## Part 2: Baseline Verification

Goal: Prove the reorganized Docker app starts and the main routes work before adding new features.

Checklist:

- [x] Confirm `.env.example` has all needed variables.
- [x] Run `docker-compose config` to validate Compose syntax.
- [x] Build services with `docker-compose build`.
- [x] Start the stack with `docker-compose up`.
- [x] Verify frontend loads at `http://localhost:3000`.
- [x] Verify API docs load at `http://localhost:8000/docs`.
- [x] Verify Flower loads at `http://localhost:5555`.
- [x] Verify backend health endpoint returns OK.

Success criteria:

- All services start cleanly.
- Backend can connect to PostgreSQL and Redis.
- Frontend can reach backend API.
- No import-path errors after the file reorganization.

Tests:

- `docker-compose config`
- Backend health check
- Manual browser/API smoke test

## Part 3: Backend Auth And Data Model Hardening

Goal: Make the auth and persistence layer stable enough for real use.

Checklist:

- [x] Review password hashing, JWT expiry, and token validation.
- [x] Confirm user uniqueness constraints work.
- [x] Confirm scrape jobs are scoped to the authenticated user.
- [x] Confirm deleting a job deletes its results.
- [x] Add database migration strategy or explicitly document current `create_all` limitation.
- [x] Add backend tests for auth, job ownership, and basic CRUD behavior.

Success criteria:

- Users can register, login, and call `/me`.
- Users cannot access or delete another user's jobs.
- Job/result persistence is reliable.
- Database initialization strategy is clear.

Tests:

- FastAPI route tests for auth.
- FastAPI route tests for scraping job CRUD.
- Model-level checks for cascade delete.

## Part 4: Scraping Job Pipeline

Goal: Validate the async job lifecycle from API request to Celery execution to saved results.

Checklist:

- [x] Start a scrape job through the API.
- [x] Confirm job begins as `pending`.
- [x] Confirm Celery updates it to `running`.
- [x] Confirm successful scrape stores results and marks job `completed`.
- [x] Confirm scraper failures mark job `failed` with a useful error message.
- [x] Confirm result records normalize likes, comments, shares, views, URLs, author, content, and published date.
- [x] Add tests around task result persistence using controlled/mock scraper outputs.

Success criteria:

- The API never blocks while scraping.
- Job status is accurate.
- Result count matches saved result rows.
- Scraper errors are visible in job detail.

Tests:

- Celery task tests with mocked scraper functions.
- API smoke test for job creation and result retrieval.

## Part 5: Free Scraper Validation

Goal: Prove each free scraper path works where possible and clearly document limitations.

Checklist:

- [x] Test Twitter/X through Nitter instances.
- [x] Test Instagram through instaloader with public profile target.
- [x] Test Reddit through PRAW credentials.
- [x] Test YouTube through yt-dlp.
- [x] Decide whether to keep or remove the limited LinkedIn free scraper from the UI.
- [x] Add timeout and failure messages that help the user understand platform limitations.
- [x] Document which free methods require credentials.

Success criteria:

- Free scrapers either return normalized results or a clear failure.
- The UI accurately shows which platforms support free mode.
- The user can run trials without paid credentials for supported platforms.

Tests:

- Unit tests for result normalization.
- Manual live smoke tests for selected public targets.
- No tests should depend on private accounts or secrets committed to the repo.

## Part 6: Paid Apify Validation

Goal: Make the paid scraping path usable and cost-transparent.

Checklist:

- [x] Confirm `APIFY_API_TOKEN` loading works from `.env`.
- [x] Validate Apify Twitter/X actor.
- [x] Validate Apify Instagram actor.
- [x] Validate Apify LinkedIn actor.
- [x] Validate Apify Facebook actor.
- [x] Validate Apify TikTok actor.
- [ ] Record rough cost and reliability notes from trial runs.
- [x] Improve error handling for missing token, actor failure, and empty datasets.

Success criteria:

- Paid mode works when a valid Apify token is configured.
- Missing token produces a clear user-facing job error.
- Cost guidance is documented before recommending production use.

Tests:

- Unit tests with mocked Apify client responses.
- Optional live smoke tests using a small max result count.

## Part 7: Dashboard And Frontend Workflow

Goal: Ensure the authenticated UI supports the full scrape workflow cleanly.

Checklist:

- [x] Verify login/register/logout behavior.
- [x] Verify dashboard stats match backend data.
- [x] Verify recent jobs link to job detail.
- [x] Verify new scrape form submits valid API payloads.
- [x] Verify platform free/paid availability controls are accurate.
- [x] Verify history search, filters, refresh, and delete.
- [x] Verify job detail auto-refresh for pending/running jobs.
- [x] Verify result cards handle long content and missing metrics.

Success criteria:

- A user can complete the full flow from registration to scraping to viewing results.
- UI state matches backend state.
- Dark dashboard remains readable and responsive.

Tests:

- Frontend build test.
- Manual browser workflow test.
- Add component or integration tests if a test runner is introduced.

## Part 8: Security, Legal, And Abuse Guardrails

Goal: Reduce operational risk before public GitHub release.

Checklist:

- [x] Ensure secrets are never committed.
- [x] Add `.env.example` documentation for every expected variable.
- [x] Add clear legal/ethics warning for public-only scraping.
- [x] Add rate-limit guidance for production.
- [x] Add max result limits on backend, not only frontend.
- [x] Validate user input for target strings and job types.
- [x] Review CORS settings before production deployment.

Success criteria:

- Public repository does not expose credentials.
- Backend enforces important limits.
- README makes platform/API limitations clear.

Tests:

- Check git status for secrets.
- Backend validation tests for invalid scrape requests.
- Manual review of README and `.env.example`.

## Part 9: Public GitHub Readiness

Goal: Prepare the project to be published as a clean public repository.

Checklist:

- [ ] Update README to match actual setup and verified commands.
- [ ] Include project structure.
- [ ] Include Docker quick start.
- [ ] Include API key setup.
- [ ] Include free vs paid scraper notes.
- [ ] Include troubleshooting for Docker, Redis, Celery, and scraper failures.
- [ ] Confirm `.gitignore` covers local env files, node modules, Python caches, build output, and database artifacts.
- [ ] Run final build/smoke checks.

Success criteria:

- A fresh user can clone, configure `.env`, run Docker Compose, and use the app.
- Documentation does not overpromise scraper reliability.
- Repo is safe to publish publicly.

Tests:

- Clean checkout style Docker build.
- Frontend build.
- Backend import/health check.

## Part 10: Future Enhancements After MVP

These are not required before the first reviewed implementation pass.

- Add scheduled recurring scrape jobs.
- Add CSV/JSON export.
- Add team accounts or admin dashboard.
- Add per-user usage limits.
- Add proxy support for fragile platforms.
- Add richer analytics over scraped content.
- Add provider abstraction if Apify is replaced or supplemented by other paid APIs.
- Add Alembic migrations for production database evolution.
- Add Playwright end-to-end tests for full browser workflows.

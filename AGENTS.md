# Social Scraper Web App

## Project Brief

This project is a Docker-based social media scraping web application.

The user request, summarized:

- Build a web app for scraping social media posts and profiles.
- The app must have login-protected dashboard access.
- The dashboard must show scraping history and allow new scrape requests.
- Support both free fallback scraping and paid scraping options.
- Target platforms include Twitter/X, Facebook, LinkedIn, Instagram, and other professional/content platforms where influencers share tips, posts, and advice.
- Use trial/free APIs or libraries first, then identify which paid options are cheapest and most reliable.
- Publish-ready public GitHub repository structure.

## Current Architecture

The codebase is organized as a full-stack Docker Compose app:

- `backend/`: FastAPI application, SQLAlchemy models, Celery worker code, scraper services.
- `frontend/`: React + Tailwind application served by Nginx in Docker.
- `docker-compose.yml`: PostgreSQL, Redis, backend, Celery worker, Flower, frontend.
- `docs/PLAN.md`: phased implementation and review plan.

Runtime services:

- PostgreSQL stores users, scrape jobs, and scrape results.
- Redis is the Celery broker/backend.
- FastAPI exposes auth, scraping, and dashboard APIs.
- Celery executes scraping jobs asynchronously.
- Flower exposes Celery monitoring on port `5555`.
- React frontend is exposed on port `3000`.
- FastAPI docs are exposed on port `8000/docs`.

## Backend Scope

Backend stack:

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT auth
- Celery
- Redis

Important backend paths:

- `backend/app/main.py`: FastAPI app setup and router registration.
- `backend/app/api/auth.py`: register, login, current user.
- `backend/app/api/scraping.py`: start/list/detail/delete jobs and fetch results.
- `backend/app/api/dashboard.py`: dashboard stats.
- `backend/app/core/config.py`: environment-based settings.
- `backend/app/core/database.py`: SQLAlchemy engine/session.
- `backend/app/core/security.py`: password hashing and JWT handling.
- `backend/app/core/celery_app.py`: Celery configuration.
- `backend/app/models/`: SQLAlchemy models.
- `backend/app/schemas/`: Pydantic schemas.
- `backend/app/services/free_scraper.py`: free/open-source scraper implementations.
- `backend/app/services/apify_scraper.py`: paid Apify scraper implementations.
- `backend/app/tasks/scrape_tasks.py`: Celery task dispatch and result persistence.

Backend API requirements:

- JWT auth: register, login, `/me`.
- Scraping API: start job, list jobs, job detail, delete job, get results, supported platforms.
- Dashboard API: total jobs, completed/failed/pending jobs, total results, platforms used, recent jobs.
- Jobs must run asynchronously through Celery, not inside request handlers.
- Job status must move through `pending`, `running`, `completed`, or `failed`.
- Scrape results must preserve engagement metrics where available: likes, comments, shares, views, published date, URL, author, content, raw data.

## Scraper Strategy

The project supports two scraping modes.

Free mode:

- Twitter/X: Nitter instances where available. Reliability may vary because public instances can be blocked or unavailable.
- Instagram: `instaloader`, public/profile-limited and rate-limited.
- Reddit: PRAW with Reddit's official free API credentials.
- YouTube: `yt-dlp`, no YouTube API key required for basic public metadata.
- LinkedIn: very limited public page scraping only; production should prefer paid providers.

Paid mode:

- Apify is the preferred first paid provider because one account can cover Twitter/X, Instagram, LinkedIn, Facebook, TikTok, and more.
- Existing service code includes Apify scrapers for Twitter/X, Instagram, LinkedIn, Facebook, and TikTok.
- Paid provider cost and reliability should be documented before recommending production use.

Implementation principle:

- Keep free fallback and paid option side by side.
- Do not make paid scraping mandatory for platforms where a free mode exists.
- For blocked or fragile platforms, return clear job errors rather than hiding failures.
- Do not scrape private, login-gated, or unauthorized content without explicit user configuration and legal review.

## Frontend Scope

Frontend stack:

- React
- Tailwind CSS
- React Router
- Axios
- Recharts
- Lucide React icons
- React Hot Toast

Important frontend paths:

- `frontend/src/App.jsx`: route definitions and auth guard.
- `frontend/src/context/AuthContext.jsx`: auth state and token persistence.
- `frontend/src/services/api.js`: Axios API client.
- `frontend/src/components/Layout.jsx`: authenticated app shell.
- `frontend/src/pages/Login.jsx`: login page.
- `frontend/src/pages/Register.jsx`: registration page.
- `frontend/src/pages/Dashboard.jsx`: stats cards, bar chart, recent jobs.
- `frontend/src/pages/NewScrape.jsx`: platform picker, job type, free/paid toggle, max results.
- `frontend/src/pages/History.jsx`: job table, filters, search, delete.
- `frontend/src/pages/JobDetail.jsx`: auto-refreshing job status and result viewer.

Frontend requirements:

- Dark dashboard UI.
- Login/register pages outside the protected layout.
- Authenticated routes behind JWT-backed auth.
- New scrape flow must clearly expose platform, job type, target, method, and max results.
- History must support filtering, search, and deletion.
- Job detail must refresh while jobs are pending/running and show result engagement stats.

## Docker Requirements

Expected services:

- `db`: PostgreSQL
- `redis`: Redis
- `backend`: FastAPI
- `worker`: Celery worker
- `flower`: Celery monitor
- `frontend`: React build served by Nginx

Primary command:

```bash
docker-compose up --build
```

Useful URLs:

- Frontend: `http://localhost:3000`
- Backend API docs: `http://localhost:8000/docs`
- Flower: `http://localhost:5555`

Environment setup:

- Copy `.env.example` to `.env`.
- Set `SECRET_KEY`.
- Set `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` for Reddit.
- Set `APIFY_API_TOKEN` for paid scraping.
- Optional Instagram credentials can be configured for `instaloader`.

## Engineering Standards

- Keep changes scoped to this scraper product. Do not add unrelated AI/Kanban/project-management features.
- Preserve the existing backend package layout under `backend/app`.
- Preserve the existing React layout under `frontend/src`.
- Prefer clear error handling over silent scraper failures.
- Keep scraping jobs asynchronous.
- Avoid adding new infrastructure unless it directly supports scraping, auth, dashboard, history, deployment, or testing.
- Before changing behavior, inspect the current route/model/schema/task interactions.
- When adding platform support, update backend platform metadata, scraper dispatch, schemas if needed, and frontend platform options together.
- Any paid provider recommendation must mention cost, reliability, and limitations.
- Public GitHub readiness means clear docs, no secrets committed, usable `.env.example`, and Docker instructions that work from a clean checkout.

## Documentation Workflow

Before implementing new work:

1. Review `docs/PLAN.md`.
2. Confirm which part is being implemented.
3. Keep implementation aligned with the plan unless the user approves a plan change.
4. Update documentation only when it reflects real project behavior or an approved plan.

The user wants to review the plan before further implementation. Do not proceed into feature changes until the plan is approved.

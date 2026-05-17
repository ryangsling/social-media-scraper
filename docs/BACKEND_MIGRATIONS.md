# Backend Migration Strategy

## Current State

Alembic is configured in `backend/` and the runtime `create_all` call has been removed. Database schema changes now go through migrations.

## How To Run Migrations

From the repo root:

- Docker:
  - `docker-compose run --rm backend alembic upgrade head`
- Local virtualenv:
  - `cd backend`
  - `alembic upgrade head`

## Migrating Existing Databases

If your database was created via `Base.metadata.create_all`, you can mark it as up-to-date without recreating tables:

- `docker-compose run --rm backend alembic stamp head`

Then run `alembic upgrade head` for future migrations.

## Recommended Direction

Use Alembic migrations as the source of truth for database changes.

Operational policy:

1. Any model change must be paired with a migration.
2. Run `alembic upgrade head` before serving API/worker traffic.
3. Avoid re-introducing `Base.metadata.create_all` in production code.

## Why This Matters

- Prevents silent schema drift between environments.
- Makes changes reviewable and rollback-aware.
- Reduces startup race conditions where multiple services create schema at once.

## Minimum Operational Policy

- Any model change must be paired with an Alembic migration.
- Deployments should run `alembic upgrade head` before serving traffic.

"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2025-02-14 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


platform_enum = sa.Enum(
    "twitter",
    "instagram",
    "linkedin",
    "facebook",
    "reddit",
    "youtube",
    "tiktok",
    "quora",
    name="platformenum",
)
status_enum = sa.Enum(
    "pending",
    "running",
    "completed",
    "failed",
    name="statusenum",
)
scrape_job_type_enum = sa.Enum(
    "profile",
    "posts",
    "hashtag",
    "keyword",
    name="scrapejobtypeenum",
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=False)

    op.create_table(
        "scrape_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("platform", platform_enum, nullable=False),
        sa.Column("job_type", scrape_job_type_enum, nullable=True),
        sa.Column("target", sa.String(), nullable=False),
        sa.Column("status", status_enum, nullable=True),
        sa.Column("method", sa.String(), nullable=True),
        sa.Column("celery_task_id", sa.String(), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_scrape_jobs_id", "scrape_jobs", ["id"], unique=False)

    op.create_table(
        "scrape_results",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "job_id", sa.Integer(), sa.ForeignKey("scrape_jobs.id"), nullable=False
        ),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=True),
        sa.Column("post_id", sa.String(), nullable=True),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("author_url", sa.String(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("likes", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Integer(), nullable=True),
        sa.Column("shares", sa.Integer(), nullable=True),
        sa.Column("views", sa.Integer(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.create_index("ix_scrape_results_id", "scrape_results", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scrape_results_id", table_name="scrape_results")
    op.drop_table("scrape_results")

    op.drop_index("ix_scrape_jobs_id", table_name="scrape_jobs")
    op.drop_table("scrape_jobs")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")

    scrape_job_type_enum.drop(op.get_bind(), checkfirst=True)
    status_enum.drop(op.get_bind(), checkfirst=True)
    platform_enum.drop(op.get_bind(), checkfirst=True)

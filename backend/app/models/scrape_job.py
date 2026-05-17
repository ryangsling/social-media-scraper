import enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PlatformEnum(str, enum.Enum):
    twitter = "twitter"
    instagram = "instagram"
    linkedin = "linkedin"
    facebook = "facebook"
    reddit = "reddit"
    youtube = "youtube"
    tiktok = "tiktok"
    quora = "quora"


class StatusEnum(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class ScrapeJobTypeEnum(str, enum.Enum):
    profile = "profile"
    posts = "posts"
    hashtag = "hashtag"
    keyword = "keyword"


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(SAEnum(PlatformEnum, name="platformenum"), nullable=False)
    job_type = Column(
        SAEnum(ScrapeJobTypeEnum, name="scrapejobtypeenum"),
        default=ScrapeJobTypeEnum.profile,
    )
    target = Column(String, nullable=False)  # username, hashtag, keyword
    status = Column(
        SAEnum(StatusEnum, name="statusenum"),
        default=StatusEnum.pending,
    )
    method = Column(String, default="free")  # free or apify
    celery_task_id = Column(String, nullable=True)
    result_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    user = relationship("User", back_populates="scrape_jobs")
    results = relationship(
        "ScrapeResult", back_populates="job", cascade="all, delete-orphan"
    )


class ScrapeResult(Base):
    __tablename__ = "scrape_results"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("scrape_jobs.id"), nullable=False)
    platform = Column(String, nullable=False)
    content_type = Column(String, default="post")  # post, profile, comment
    post_id = Column(String, nullable=True)
    author = Column(String, nullable=True)
    author_url = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), nullable=True)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    job = relationship("ScrapeJob", back_populates="results")

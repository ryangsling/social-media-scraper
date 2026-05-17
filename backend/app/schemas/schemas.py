from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.scrape_job import PlatformEnum, ScrapeJobTypeEnum, StatusEnum


# Auth
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Username cannot be empty")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# Scraping
class ScrapeRequest(BaseModel):
    platform: PlatformEnum
    job_type: ScrapeJobTypeEnum = ScrapeJobTypeEnum.profile
    target: str = Field(min_length=1, max_length=120)
    use_apify: bool = False
    max_results: int = Field(default=50, ge=10, le=500)

    @field_validator("target")
    @classmethod
    def validate_target(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Target cannot be empty")
        return value


class ScrapeResultOut(BaseModel):
    id: int
    platform: str
    content_type: str
    post_id: Optional[str]
    author: Optional[str]
    author_url: Optional[str]
    content: Optional[str]
    url: Optional[str]
    likes: int
    comments: int
    shares: int
    views: int
    published_at: Optional[datetime]
    created_at: datetime
    raw_data: Optional[dict] = None
    model_config = ConfigDict(from_attributes=True)


class ScrapeJobOut(BaseModel):
    id: int
    platform: str
    job_type: str
    target: str
    status: str
    method: str
    result_count: int
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class ScrapeJobDetail(ScrapeJobOut):
    results: List[ScrapeResultOut] = []


# Dashboard
class DashboardStats(BaseModel):
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    pending_jobs: int
    total_results: int
    platforms_used: List[str]
    recent_jobs: List[ScrapeJobOut]

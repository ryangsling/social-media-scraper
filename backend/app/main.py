from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, dashboard, scraping
from app.core.config import settings

app = FastAPI(
    title="Social Media Scraper",
    description="Scrape social media profiles and posts",
    version="1.0.0",
)

cors_origins = [
    o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",") if o.strip()
]
allow_all_origins = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["http://localhost:3000"],
    # Credentials + wildcard origins are not valid together in browsers.
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["Scraping"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/health")
def health():
    return {"status": "ok"}

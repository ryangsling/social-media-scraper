"""
Free scraping services using open-source libraries.
These have rate limits and may break if platforms change their structure.
"""
import httpx
import json
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from app.core.config import settings


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def _sleep():
    time.sleep(random.uniform(1.5, 3.5))


# ─────────────────────────────────────────────
# TWITTER / X  (Nitter fallback)
# ─────────────────────────────────────────────
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.1d4.us",
]

def scrape_twitter_free(username: str, max_results: int = 50) -> List[Dict[str, Any]]:
    results = []
    for base in NITTER_INSTANCES:
        try:
            url = f"{base}/{username.lstrip('@')}"
            resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            tweets = soup.select(".timeline-item")
            for tw in tweets[:max_results]:
                content_el = tw.select_one(".tweet-content")
                stats = tw.select(".tweet-stat")
                def stat(i):
                    try:
                        return int("".join(filter(str.isdigit, stats[i].get_text())) or "0")
                    except Exception:
                        return 0
                date_el = tw.select_one(".tweet-date a")
                link = date_el["href"] if date_el else ""
                results.append({
                    "platform": "twitter",
                    "content_type": "post",
                    "author": username,
                    "content": content_el.get_text(strip=True) if content_el else "",
                    "url": f"https://twitter.com{link}" if link else "",
                    "likes": stat(1),
                    "comments": stat(0),
                    "shares": stat(2),
                    "views": 0,
                    "published_at": None,
                    "raw_data": {},
                })
            if results:
                break
        except Exception:
            continue
    if not results:
        return [{
            "error": (
                "Twitter free scrape failed across available Nitter instances. "
                "Try again later or use Apify for better reliability."
            ),
            "platform": "twitter",
        }]
    return results


# ─────────────────────────────────────────────
# INSTAGRAM  (instaloader — public profiles)
# ─────────────────────────────────────────────
def scrape_instagram_free(username: str, max_results: int = 30) -> List[Dict[str, Any]]:
    try:
        import instaloader
        L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            save_metadata=False,
            compress_json=False,
        )
        if settings.INSTAGRAM_USERNAME and settings.INSTAGRAM_PASSWORD:
            L.login(settings.INSTAGRAM_USERNAME, settings.INSTAGRAM_PASSWORD)

        profile = instaloader.Profile.from_username(L.context, username)
        results = []
        for post in profile.get_posts():
            if len(results) >= max_results:
                break
            results.append({
                "platform": "instagram",
                "content_type": "post",
                "post_id": post.shortcode,
                "author": username,
                "content": post.caption or "",
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                "likes": post.likes,
                "comments": post.comments,
                "shares": 0,
                "views": post.video_view_count if post.is_video else 0,
                "published_at": post.date_utc.isoformat() if post.date_utc else None,
                "raw_data": {"hashtags": list(post.caption_hashtags)},
            })
            _sleep()
        return results
    except Exception as e:
        return [{"error": str(e), "platform": "instagram"}]


# ─────────────────────────────────────────────
# REDDIT  (official free API via PRAW)
# ─────────────────────────────────────────────
def scrape_reddit_free(target: str, job_type: str = "profile", max_results: int = 50) -> List[Dict[str, Any]]:
    try:
        if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
            return [{
                "error": (
                    "Reddit credentials missing. Set REDDIT_CLIENT_ID and "
                    "REDDIT_CLIENT_SECRET in .env."
                ),
                "platform": "reddit",
            }]
        import praw
        reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
        )
        results = []
        if job_type == "profile":
            redditor = reddit.redditor(target)
            for submission in redditor.submissions.new(limit=max_results):
                results.append({
                    "platform": "reddit",
                    "content_type": "post",
                    "post_id": submission.id,
                    "author": str(submission.author),
                    "content": f"{submission.title}\n{submission.selftext}",
                    "url": f"https://reddit.com{submission.permalink}",
                    "likes": submission.score,
                    "comments": submission.num_comments,
                    "shares": 0,
                    "views": 0,
                    "published_at": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                    "raw_data": {"subreddit": submission.subreddit.display_name},
                })
        elif job_type in ("keyword", "hashtag"):
            for submission in reddit.subreddit("all").search(target, limit=max_results):
                results.append({
                    "platform": "reddit",
                    "content_type": "post",
                    "post_id": submission.id,
                    "author": str(submission.author),
                    "content": f"{submission.title}\n{submission.selftext}",
                    "url": f"https://reddit.com{submission.permalink}",
                    "likes": submission.score,
                    "comments": submission.num_comments,
                    "shares": 0,
                    "views": 0,
                    "published_at": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                    "raw_data": {"subreddit": submission.subreddit.display_name},
                })
        return results
    except Exception as e:
        return [{"error": str(e), "platform": "reddit"}]


# ─────────────────────────────────────────────
# LINKEDIN  (basic public scrape via httpx)
# Note: LinkedIn heavily blocks scrapers. Use Apify for production.
# ─────────────────────────────────────────────
def scrape_linkedin_free(username: str, max_results: int = 20) -> List[Dict[str, Any]]:
    try:
        url = f"https://www.linkedin.com/in/{username}/"
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        soup = BeautifulSoup(resp.text, "lxml")
        name_el = soup.select_one("h1")
        headline_el = soup.select_one(".top-card-layout__headline")
        return [{
            "platform": "linkedin",
            "content_type": "profile",
            "author": name_el.get_text(strip=True) if name_el else username,
            "content": headline_el.get_text(strip=True) if headline_el else "Profile scraped (limited data without login)",
            "url": url,
            "likes": 0, "comments": 0, "shares": 0, "views": 0,
            "published_at": None,
            "raw_data": {"note": "LinkedIn requires Apify for full post data"},
        }]
    except Exception as e:
        return [{"error": str(e), "platform": "linkedin"}]


# ─────────────────────────────────────────────
# YOUTUBE  (via yt-dlp metadata, no API key)
# ─────────────────────────────────────────────
def scrape_youtube_free(channel: str, max_results: int = 20) -> List[Dict[str, Any]]:
    try:
        import subprocess, json as _json
        cmd = [
            "yt-dlp", "--flat-playlist", "--dump-json",
            "--playlist-end", str(max_results),
            f"https://www.youtube.com/@{channel}/videos"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            return [{
                "error": (
                    f"YouTube free scrape failed via yt-dlp: "
                    f"{(proc.stderr or 'unknown error').strip()}"
                ),
                "platform": "youtube",
            }]
        results = []
        for line in proc.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                v = _json.loads(line)
                results.append({
                    "platform": "youtube",
                    "content_type": "video",
                    "post_id": v.get("id", ""),
                    "author": v.get("channel", channel),
                    "content": v.get("title", ""),
                    "url": f"https://www.youtube.com/watch?v={v.get('id', '')}",
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "views": v.get("view_count", 0) or 0,
                    "published_at": None,
                    "raw_data": {"duration": v.get("duration"), "thumbnail": v.get("thumbnail")},
                })
            except Exception:
                continue
        return results
    except Exception as e:
        return [{"error": str(e), "platform": "youtube"}]

"""
Apify-based scraping — reliable, paid, production-ready.
Apify pricing: https://apify.com/pricing  (starts ~$49/mo)
"""

from typing import Any, Dict, List

from app.core.config import settings


def _get_client():
    from apify_client import ApifyClient

    if not settings.APIFY_API_TOKEN:
        raise ValueError("APIFY_API_TOKEN not set. Add it to your .env file.")
    return ApifyClient(settings.APIFY_API_TOKEN)


# ─────────────────────────────────────────────
# TWITTER via Apify  (Actor: apidojo/tweet-scraper)
# ─────────────────────────────────────────────
def _normalize_twitter_item(
    item: Dict[str, Any], fallback_author: str
) -> Dict[str, Any]:
    author = (
        item.get("author", {}).get("userName")
        or item.get("user", {}).get("username")
        or fallback_author
    )
    content = item.get("fullText") or item.get("text") or item.get("content") or ""
    url = (
        item.get("url")
        or item.get("tweetUrl")
        or item.get("twitterUrl")
        or item.get("link")
        or ""
    )
    return {
        "platform": "twitter",
        "content_type": "post",
        "post_id": item.get("id", ""),
        "author": author,
        "content": content,
        "url": url,
        "likes": item.get("likeCount", 0),
        "comments": item.get("replyCount", 0),
        "shares": item.get("retweetCount", 0),
        "views": item.get("viewCount", 0),
        "published_at": item.get("createdAt"),
        "raw_data": item,
    }


def scrape_twitter_apify(username: str, max_results: int = 100) -> List[Dict[str, Any]]:
    client = _get_client()
    run = client.actor("apidojo/tweet-scraper").call(
        run_input={
            "startUrls": [{"url": f"https://twitter.com/{username.lstrip('@')}"}],
            "maxItems": max_results,
            "addUserInfo": True,
        }
    )
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(_normalize_twitter_item(item, username))
    return results


def scrape_twitter_apify_search(
    term: str, max_results: int = 100
) -> List[Dict[str, Any]]:
    client = _get_client()
    run = client.actor("apidojo/tweet-scraper").call(
        run_input={
            "searchTerms": [term],
            "maxItems": max_results,
            "addUserInfo": True,
        }
    )
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(_normalize_twitter_item(item, term.lstrip("#") or term))
    return results


# ─────────────────────────────────────────────
# INSTAGRAM via Apify  (Actor: apify/instagram-scraper)
# ─────────────────────────────────────────────
def scrape_instagram_apify(
    username: str, max_results: int = 50
) -> List[Dict[str, Any]]:
    client = _get_client()
    run = client.actor("apify/instagram-scraper").call(
        run_input={
            "directUrls": [f"https://www.instagram.com/{username}/"],
            "resultsType": "posts",
            "resultsLimit": max_results,
        }
    )
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        content = item.get("caption") or item.get("text") or item.get("title") or ""
        url = item.get("url") or item.get("shortCode")
        if url and not url.startswith("http"):
            url = f"https://www.instagram.com/p/{url}/"
        results.append(
            {
                "platform": "instagram",
                "content_type": "post",
                "post_id": item.get("shortCode", ""),
                "author": item.get("ownerUsername", username),
                "content": content,
                "url": url or "",
                "likes": item.get("likesCount", 0),
                "comments": item.get("commentsCount", 0),
                "shares": 0,
                "views": item.get("videoViewCount", 0),
                "published_at": item.get("timestamp"),
                "raw_data": item,
            }
        )
    return results


# ─────────────────────────────────────────────
# LINKEDIN via Apify  (Actor: curious_coder/linkedin-profile-scraper)
# ─────────────────────────────────────────────
def scrape_linkedin_apify(username: str, max_results: int = 20) -> List[Dict[str, Any]]:
    client = _get_client()
    run = client.actor("curious_coder/linkedin-profile-scraper").call(
        run_input={
            "profileUrls": [f"https://www.linkedin.com/in/{username}/"],
            "maxDelay": 5,
        }
    )
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        content = item.get("summary") or item.get("headline") or item.get("about") or ""
        profile_url = (
            item.get("profileUrl") or f"https://www.linkedin.com/in/{username}/"
        )
        results.append(
            {
                "platform": "linkedin",
                "content_type": "profile",
                "post_id": None,
                "author": item.get("fullName", username),
                "content": content,
                "url": profile_url,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "views": 0,
                "published_at": None,
                "raw_data": item,
            }
        )
    return results


# ─────────────────────────────────────────────
# FACEBOOK via Apify  (Actor: apify/facebook-posts-scraper)
# ─────────────────────────────────────────────
def scrape_facebook_apify(target: str, max_results: int = 50) -> List[Dict[str, Any]]:
    client = _get_client()
    run = client.actor("apify/facebook-posts-scraper").call(
        run_input={
            "startUrls": [{"url": f"https://www.facebook.com/{target}"}],
            "resultsLimit": max_results,
        }
    )
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        content = item.get("text") or item.get("message") or item.get("story") or ""
        url = item.get("url") or item.get("postUrl") or ""
        results.append(
            {
                "platform": "facebook",
                "content_type": "post",
                "post_id": item.get("postId", ""),
                "author": item.get("pageName", target),
                "content": content,
                "url": url,
                "likes": item.get("likes", 0),
                "comments": item.get("comments", 0),
                "shares": item.get("shares", 0),
                "views": 0,
                "published_at": item.get("time"),
                "raw_data": item,
            }
        )
    return results


# ─────────────────────────────────────────────
# TIKTOK via Apify  (Actor: clockworks/tiktok-scraper)
# ─────────────────────────────────────────────
def scrape_tiktok_apify(username: str, max_results: int = 50) -> List[Dict[str, Any]]:
    client = _get_client()
    run = client.actor("clockworks/tiktok-scraper").call(
        run_input={
            "profiles": [username.lstrip("@")],
            "resultsPerPage": max_results,
            "shouldDownloadCovers": False,
            "shouldDownloadVideos": False,
        }
    )
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        content = item.get("text") or item.get("description") or item.get("title") or ""
        url = (
            item.get("webVideoUrl")
            or item.get("videoUrl")
            or item.get("shareUrl")
            or ""
        )
        results.append(
            {
                "platform": "tiktok",
                "content_type": "video",
                "post_id": item.get("id", ""),
                "author": item.get("authorMeta", {}).get("name", username),
                "content": content,
                "url": url,
                "likes": item.get("diggCount", 0),
                "comments": item.get("commentCount", 0),
                "shares": item.get("shareCount", 0),
                "views": item.get("playCount", 0),
                "published_at": None,
                "raw_data": item,
            }
        )
    return results

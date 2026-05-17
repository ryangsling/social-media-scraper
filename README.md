# Social Scraper: Your Personal Social Media Intelligence Platform

Tired of clunky, ad-filled interfaces for social media? Social Scraper is a sleek, self-hosted platform that lets you scrape and analyze public social media content with ease. It features a clean, modern dashboard, asynchronous scraping jobs, and support for both free and paid scraping methods.

It's the perfect tool for researchers, marketers, and data enthusiasts who want to collect and analyze social media data without the noise.

![New Dashboard Design](https://i.imgur.com/placeholder.png) 

## Key Features

*   **Modern, Professional UI**: A completely redesigned, light-themed interface that's a joy to use.
*   **Secure Authentication**: JWT-based login and registration to keep your data safe.
*   **Intuitive Dashboard**: Get a quick overview of your scraping activity with stats, charts, and recent jobs.
*   **Flexible Scraping**: Configure scrapes by platform, job type, and target, with support for both free and paid methods.
*   **Detailed Job History**: Easily track, search, and manage all your past scraping jobs.
*   **Rich Results Viewer**: Browse and analyze your scraped data with a clean, card-based interface.
*   **Asynchronous Scraping**: Powered by Celery and Redis, so you can fire and forget your scraping jobs.
*   **Real-time Monitoring**: Keep an eye on your Celery tasks with the built-in Flower dashboard.
*   **Docker-Powered**: Get up and running in minutes with a single `docker-compose` command.

## Supported Platforms

| Platform | Free (Fallback) | Paid (Apify) | Notes |
|---|---|---|---|
| Twitter/X | ✅ | ✅ | Free via Nitter (can be unstable). |
| Instagram | ✅ | ✅ | Free via `instaloader` (public profiles only). |
| Reddit | ✅ | — | Uses the official free API (PRAW). |
| YouTube | ✅ | — | via `yt-dlp` (no API key needed). |
| LinkedIn | ⚠️ Limited | ✅ | Free scraping is limited to public profiles. Use Apify for best results. |
| Facebook | ❌ | ✅ | Requires a paid Apify plan. |
| TikTok | ❌ | ✅ | Requires a paid Apify plan. |
| Quora | ❌ | ❌ | Not yet implemented. |

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/social-scraper.git
cd social-scraper
```

### 2. Configure Your Environment

Copy the example `.env` file and fill in your details:

```bash
cp .env.example .env
```

You'll need to set a `SECRET_KEY` for the backend. For the free scrapers, you'll need API keys for Reddit. For the paid scrapers, you'll need an Apify API token.

### 3. Run the Migrations

```bash
docker-compose run --rm backend alembic upgrade head
```

### 4. Launch the Application

```bash
docker-compose up --build
```

### 5. You're Ready to Go!

| Service | URL |
|---|---|
| **Frontend** | `http://localhost:3000` |
| Backend API | `http://localhost:8000/docs` |
| Flower | `http://localhost:5555` |

## Contributing

We love contributions! If you have an idea for a new feature or have found a bug, please open an issue or submit a pull request.

## Legal & Ethics

*   Only scrape publicly available content.
*   Always respect each platform’s Terms of Service.
*   Do not use this tool for spam, harassment, or commercial data resale.
*   This tool is intended for research and personal use only.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

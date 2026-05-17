"""
AI News Hub — Automated News Pipeline
Fetches news from RSS + DuckDuckGo, rewrites with Gemini AI in 3 languages,
and POSTs to the FastAPI backend.

Run: python scripts/main.py
Env: GEMINI_API_KEY, API_URL
"""

import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests

try:
    from google import genai
except ImportError:
    print("❌ google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("❌ duckduckgo_search not installed. Run: pip install duckduckgo_search")
    sys.exit(1)

# ────────────────────────── Configuration ──────────────────────────

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
API_URL = os.environ.get("API_URL", "http://localhost:8000")

POSTED_TITLES_FILE = Path(__file__).parent / "posted_titles.json"
MAX_POSTED_TITLES = 500  # Keep last N titles to avoid unbounded growth

# Headlines to fetch per source
HEADLINES_PER_SOURCE = 3

# ── RSS Feed Sources (Google News RSS) ──
RSS_FEEDS = {
    "politics": [
        "https://news.google.com/rss/topics/CAAqBwgKMIHWlgswrNaxAw?hl=hi&gl=IN&ceid=IN:hi",  # Hindi politics
        "https://news.google.com/rss/topics/CAAqBwgKMIHWlgswrNaxAw?hl=en-IN&gl=IN&ceid=IN:en",  # English politics India
    ],
    "sports": [
        "https://news.google.com/rss/topics/CAAqBwgKMKHL9QowhZa5Ag?hl=hi&gl=IN&ceid=IN:hi",  # Hindi sports
        "https://news.google.com/rss/topics/CAAqBwgKMKHL9QowhZa5Ag?hl=en-IN&gl=IN&ceid=IN:en",  # English sports India
    ],
    "entertainment": [
        "https://news.google.com/rss/topics/CAAqBwgKMJzMtAowkKy0Ag?hl=hi&gl=IN&ceid=IN:hi",  # Hindi entertainment
        "https://news.google.com/rss/topics/CAAqBwgKMJzMtAowkKy0Ag?hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "jobs": [
        "https://news.google.com/rss/search?q=sarkari+naukri+result+india&hl=hi&gl=IN&ceid=IN:hi",
        "https://news.google.com/rss/search?q=government+jobs+india+2024&hl=en-IN&gl=IN&ceid=IN:en",
    ],
}

# DuckDuckGo search queries for local news
DDG_QUERIES = {
    "local": [
        "Lucknow breaking news today",
        "Lucknow ताजा खबर आज",
    ],
}


# ────────────────────────── Gemini Setup ──────────────────────────

def setup_gemini():
    """Configure the Gemini AI model."""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set.")
        sys.exit(1)
    client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1'})
    return client


# ────────────────────────── Title Tracking ──────────────────────────

def load_posted_titles() -> set:
    """Load previously posted titles to avoid duplicates."""
    if POSTED_TITLES_FILE.exists():
        try:
            data = json.loads(POSTED_TITLES_FILE.read_text(encoding="utf-8"))
            return set(data)
        except (json.JSONDecodeError, TypeError):
            return set()
    return set()


def save_posted_titles(titles: set):
    """Save posted titles (keep only the most recent ones)."""
    title_list = list(titles)
    if len(title_list) > MAX_POSTED_TITLES:
        title_list = title_list[-MAX_POSTED_TITLES:]
    POSTED_TITLES_FILE.write_text(
        json.dumps(title_list, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ────────────────────────── News Fetching ──────────────────────────

def fetch_rss_headlines(feed_urls: list, max_items: int = HEADLINES_PER_SOURCE) -> list:
    """Fetch headlines from RSS feeds."""
    headlines = []
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                headlines.append({
                    "title": entry.get("title", "").strip(),
                    "summary": entry.get("summary", entry.get("description", "")).strip(),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                })
        except Exception as e:
            print(f"  ⚠️  RSS error for {url}: {e}")
    return headlines


def fetch_ddg_headlines(queries: list, max_results: int = HEADLINES_PER_SOURCE) -> list:
    """Fetch headlines using DuckDuckGo search."""
    headlines = []
    for query in queries:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=max_results, region="in-en"))
                for r in results:
                    headlines.append({
                        "title": r.get("title", "").strip(),
                        "summary": r.get("body", "").strip(),
                        "link": r.get("url", ""),
                        "published": r.get("date", ""),
                    })
        except Exception as e:
            print(f"  ⚠️  DDG error for '{query}': {e}")
    return headlines


# ────────────────────────── AI Article Generation ──────────────────────────

GEMINI_PROMPT_TEMPLATE = """You are a professional multilingual news writer for an Indian news website.

Given the following raw news headline and snippet, write a comprehensive, SEO-friendly news article of approximately 200 words in THREE languages: Hindi, English, and Marathi.

**Raw headline:** {title}
**Raw snippet:** {summary}
**Category:** {category}

**Output Requirements:**
1. Rewrite the news — do NOT copy the raw text verbatim. Add context and analysis.
2. Use SEO-friendly, engaging titles.
3. Each article body should be ~200 words, informative, and neutral in tone.
4. Output ONLY valid JSON (no markdown fences, no extra text).

**Output JSON format (strictly follow this):**
{{
  "id": "{article_id}",
  "category": "{category}",
  "content": {{
    "hi": {{
      "title": "Hindi title here",
      "body": "Hindi article body here (~200 words)"
    }},
    "en": {{
      "title": "English title here",
      "body": "English article body here (~200 words)"
    }},
    "mr": {{
      "title": "Marathi title here",
      "body": "Marathi article body here (~200 words)"
    }}
  }}
}}
"""


def generate_article(client, headline: dict, category: str) -> dict | None:
    """Use Gemini to generate a multilingual article from a raw headline."""
    article_id = uuid.uuid4().hex[:8]
    prompt = GEMINI_PROMPT_TEMPLATE.format(
        title=headline["title"],
        summary=headline.get("summary", ""),
        category=category,
        article_id=article_id,
    )

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        raw_text = response.text.strip()

        # Clean up potential markdown fences
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)

        article = json.loads(raw_text)

        # Validate structure
        if "content" not in article or "id" not in article:
            print(f"  ⚠️  Invalid structure from Gemini for: {headline['title'][:60]}")
            return None

        # Ensure category is set
        article["category"] = category
        return article

    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON parse error: {e}")
        print(f"     Raw response (first 200 chars): {raw_text[:200]}")
        return None
    except Exception as e:
        print(f"  ⚠️  Gemini error: {e}")
        return None


# ────────────────────────── Backend API Client ──────────────────────────

def post_article(article: dict) -> bool:
    """POST an article to the FastAPI backend."""
    try:
        resp = requests.post(
            f"{API_URL}/articles",
            json=article,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "duplicate":
                print(f"  ⏭️  Duplicate: {article['id']}")
            else:
                print(f"  ✅ Posted: {article['id']}")
            return True
        else:
            print(f"  ❌ POST failed ({resp.status_code}): {resp.text[:200]}")
            return False
    except requests.RequestException as e:
        print(f"  ❌ Network error: {e}")
        return False


# ────────────────────────── Main Pipeline ──────────────────────────

def run_pipeline():
    """Execute the full news pipeline."""
    print("=" * 60)
    print(f"🚀 AI News Hub Pipeline — {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    client = setup_gemini()
    posted_titles = load_posted_titles()
    new_articles = 0
    skipped = 0

    # ── Process RSS-based categories ──
    for category, feed_urls in RSS_FEEDS.items():
        print(f"\n📂 Category: {category.upper()}")
        headlines = fetch_rss_headlines(feed_urls)
        print(f"   Found {len(headlines)} headlines")

        for hl in headlines:
            raw_title = hl["title"]
            if raw_title in posted_titles:
                print(f"  ⏭️  Already processed: {raw_title[:50]}...")
                skipped += 1
                continue

            print(f"  📝 Generating article for: {raw_title[:60]}...")
            article = generate_article(client, hl, category)

            if article:
                if post_article(article):
                    posted_titles.add(raw_title)
                    new_articles += 1

            # Rate limiting — Gemini free tier has 15 RPM
            time.sleep(5)

    # ── Process DuckDuckGo-based categories (local news) ──
    for category, queries in DDG_QUERIES.items():
        print(f"\n📂 Category: {category.upper()}")
        headlines = fetch_ddg_headlines(queries)
        print(f"   Found {len(headlines)} headlines")

        for hl in headlines:
            raw_title = hl["title"]
            if raw_title in posted_titles:
                print(f"  ⏭️  Already processed: {raw_title[:50]}...")
                skipped += 1
                continue

            print(f"  📝 Generating article for: {raw_title[:60]}...")
            article = generate_article(client, hl, category)

            if article:
                if post_article(article):
                    posted_titles.add(raw_title)
                    new_articles += 1

            time.sleep(5)

    # ── Save state ──
    save_posted_titles(posted_titles)

    print("\n" + "=" * 60)
    print(f"✅ Pipeline complete!")
    print(f"   New articles: {new_articles}")
    print(f"   Skipped (duplicates): {skipped}")
    print(f"   Total tracked titles: {len(posted_titles)}")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()

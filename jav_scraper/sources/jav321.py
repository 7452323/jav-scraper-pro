"""Jav321 scraper (jav321.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

SEARCH_URL = "https://www.jav321.com/search"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from Jav321 via POST search."""
    num = number.upper()

    # Jav321 uses POST form data
    import urllib.parse
    post_data = urllib.parse.urlencode({"sn": num})
    html = fetch_text(
        SEARCH_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.jav321.com/",
        },
    )
    if not html:
        return None

    # POST via fetch_text doesn't support data; let's use the requests session directly
    import requests
    from jav_scraper.http_client import get_session
    try:
        session = get_session()
        resp = session.post(
            SEARCH_URL,
            data={"sn": num},
            headers={
                "Referer": "https://www.jav321.com/",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
            },
            timeout=30,
        )
        resp.raise_for_status()
        html = resp.text
    except Exception:
        return None

    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="jav321",
        image_cut="right",
    )

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    h1_match = re.search(
        r'<h1[^>]*>\\s*([^<]+)\\s*</h1>', html, re.IGNORECASE
    )
    if h1_match:
        t = h1_match.group(1).strip()
        if t and len(t) > 3:
            meta.title_jp = t

    # Cover
    cover_match = re.search(
        r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*img-responsive[^"]*"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Actors
    actor_links = re.findall(
        r'<a[^>]*href="/star/[^"]+"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    for name in actor_links:
        name = name.strip()
        if name:
            meta.actors.append(Actor(name=name, role="actor"))

    # Release date
    date_match = re.search(
        r'発売日[：:]\\s*([^<\\s]+)', html, re.IGNORECASE
    )
    if date_match:
        meta.release = date_match.group(1).strip()

    # Runtime
    runtime_match = re.search(
        r'収録時間[：:]\\s*(\\d+)', html, re.IGNORECASE
    )
    if runtime_match:
        meta.runtime = runtime_match.group(1).strip()

    # Director
    dir_match = re.search(
        r'監督[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if dir_match:
        meta.director = dir_match.group(1).strip()

    # Studio / Maker
    studio_match = re.search(
        r'メーカー[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if studio_match:
        meta.studio = studio_match.group(1).strip()
        meta.maker = meta.studio

    # Series
    series_match = re.search(
        r'シリーズ[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if series_match:
        meta.series = series_match.group(1).strip()

    # Tags
    tags = re.findall(
        r'<a[^>]*href="/category/[^"]+"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    # Description
    desc_match = re.search(
        r'<div[^>]*class="[^"]*sample-text[^"]*"[^>]*>\\s*(.*?)</div>',
        html, re.IGNORECASE | re.DOTALL
    )
    if not desc_match:
        desc_match = re.search(
            r'<meta\\s+name="description"[^>]*content="([^"]+)"',
            html, re.IGNORECASE
        )
    if desc_match:
        desc = desc_match.group(1).strip()
        if desc:
            desc = re.sub(r'<[^>]+>', '', desc)
            meta.plot = desc.strip()

    # Return None if no data was actually scraped
    if not meta.title_jp and not meta.cover_url:
        return None
    return meta

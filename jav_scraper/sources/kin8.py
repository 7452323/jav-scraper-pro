"""Kin8 Tengoku scraper (kin8tengoku.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://www.kin8tengoku.com"


def _derive_key(number: str) -> str:
    """Derive a movie key from the number. Kin8 uses obfuscated keys."""
    # Common pattern: lowercase, replace hyphen
    return number.lower().replace("-", "")


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from Kin8 Tengoku."""
    num = number.upper()
    key = _derive_key(num)

    # Try different key patterns
    urls = [
        f"{BASE_URL}/moviepages/{key}/index.html",
        f"{BASE_URL}/moviepages/{key.lower()}/index.html",
        f"{BASE_URL}/moviepages/{num.lower()}/index.html",
    ]
    html = ""
    for url in urls:
        html = fetch_text(url)
        if html:
            break

    if not html:
        # Try search
        search_url = f"{BASE_URL}/search/list?keyword={num}"
        html = fetch_text(search_url)
        if not html:
            return None

        # Extract first result link
        match = re.search(
            r'<a\\s+href="(/moviepages/[^"]+)"',
            html, re.IGNORECASE
        )
        if not match:
            return None

        href = match.group(1)
        if href.startswith("/"):
            href = BASE_URL + href
        html = fetch_text(href)
        if not html:
            return None

    meta = JavMetadata(
        number=num,
        source="kin8",
        image_cut="right",
    )

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        meta.title_jp = re.sub(
            r'\\s*[-–|]\\s*Kin8.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    h1_match = re.search(
        r'<h1[^>]*>\\s*([^<]+)\\s*</h1>', html, re.IGNORECASE
    )
    if h1_match:
        t = h1_match.group(1).strip()
        if t and len(t) > 3:
            meta.title_jp = t

    # Cover
    cover_match = re.search(
        r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*movie_image[^"]*"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*src="([^"]*jpgs/[^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Actors
    actor_text = re.search(
        r'出演[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if actor_text:
        names = re.split(r'[、,，/]', actor_text.group(1).strip())
        for name in names:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # Release date
    date_match = re.search(
        r'(\\d{4}[/-]\\d{2}[/-]\\d{2})', html
    )
    if date_match:
        meta.release = date_match.group(1).strip().replace("/", "-")

    # Runtime
    runtime_match = re.search(
        r'(\\d+)\\s*分', html
    )
    if runtime_match:
        meta.runtime = runtime_match.group(1).strip()

    # Director
    dir_match = re.search(
        r'監督[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if dir_match:
        meta.director = dir_match.group(1).strip()

    # Tags
    tags = re.findall(
        r'<a[^>]*href="/search/list\\?keyword=[^"]*"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    return meta

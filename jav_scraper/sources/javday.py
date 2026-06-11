"""JavDay scraper (javday.tv)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://javday.tv"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from JavDay."""
    num = number.upper()

    # Search for the number
    search_url = f"{BASE_URL}/?s={num.lower()}"
    html = fetch_text(search_url)
    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="javday",
        image_cut="right",
    )

    # Try to find the first result link
    match = re.search(
        r'<a\\s+href="([^"]+)"[^>]*title="[^"]*' + re.escape(num) + r'[^"]*"',
        html, re.IGNORECASE
    )
    if not match:
        match = re.search(
            r'<a\\s+href="([^"]+)"[^>]*class="[^"]*post-title[^"]*"[^>]*>([^<]+)',
            html, re.IGNORECASE
        )
    if not match:
        match = re.search(
            r'<a\\s+href="([^"]+)"[^>]*>([^<]*)' + re.escape(num) + r'[^<]*</a>',
            html, re.IGNORECASE
        )

    if match:
        href = match.group(1)
        if href.startswith("/"):
            href = BASE_URL + href
        html = fetch_text(href)
        if not html:
            return meta

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        meta.title_jp = re.sub(
            r'\\s*[-–|]\\s*JavDay.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    # Better title from h1
    h1_match = re.search(
        r'<h1[^>]*class="[^"]*entry-title[^"]*"[^>]*>\\s*([^<]+)',
        html, re.IGNORECASE
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
            r'<img[^>]*class="[^"]*wp-post-image[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Actors
    actor_spans = re.findall(
        r'出演[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if actor_spans:
        names = re.split(r'[、,，/]', actor_spans[0].strip())
        for name in names:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # Tags
    tags = re.findall(
        r'<a[^>]*rel="tag"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    if not meta.tags:
        tags = re.findall(
            r'<a[^>]*href="[^"]*tag[^"]*"[^>]*>([^<]+)</a>',
            html, re.IGNORECASE
        )
        meta.tags = [t.strip() for t in tags if t.strip()]

    return meta

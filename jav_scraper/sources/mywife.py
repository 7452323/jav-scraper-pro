"""MyWife scraper (mywife.jp)."""

import re
import urllib.parse

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://mywife.jp"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from MyWife."""
    num = number.upper()

    # Search
    search_url = f"{BASE_URL}/?s={urllib.parse.quote(num)}"
    html = fetch_text(search_url)
    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="mywife",
        image_cut="right",
    )

    # Title from search
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    # Find first result link
    match = re.search(
        r'<a\\s+href="([^"]+)"[^>]*>\\s*<img[^>]*alt="[^"]*' +
        re.escape(num) + r'[^"]*"',
        html, re.IGNORECASE
    )
    if not match:
        match = re.search(
            r'<a\\s+href="([^"]+)"[^>]*class="[^"]*entry-title[^"]*"',
            html, re.IGNORECASE
        )

    if match:
        href = match.group(1)
        if href.startswith("/"):
            href = BASE_URL + href
        detail_html = fetch_text(href)
        if detail_html:
            html = detail_html

    # Better title
    h1_match = re.search(
        r'<h1[^>]*class="[^"]*entry-title[^"]*"[^>]*>\\s*([^<]+)',
        html, re.IGNORECASE
    )
    if not h1_match:
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
            r'<img[^>]*class="[^"]*wp-post-image[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*class="[^"]*attachment-[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Actors
    actor_text = re.search(
        r'(?:出演|女優)[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if actor_text:
        names = re.split(r'[、,，/]', actor_text.group(1).strip())
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

    return meta

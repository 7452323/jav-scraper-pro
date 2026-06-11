"""Lulubar scraper (lulubar.co)."""

import re
import urllib.parse

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://lulubar.co"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from Lulubar."""
    num = number.upper()

    # Search
    search_url = f"{BASE_URL}/video/bysearch?search={urllib.parse.quote(num)}&page=1"
    html = fetch_text(search_url)
    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="lulubar",
        image_cut="right",
    )

    # Find first result link
    match = re.search(
        r'<a\\s+href="([^"]+)"[^>]*>\\s*<img[^>]*alt="[^"]*' +
        re.escape(num) + r'[^"]*"',
        html, re.IGNORECASE
    )
    if not match:
        match = re.search(
            r'<a\\s+href="(/video/[^"]+)"',
            html, re.IGNORECASE
        )

    if match:
        href = match.group(1)
        if href.startswith("/"):
            href = BASE_URL + href
        detail_html = fetch_text(href)
        if detail_html:
            html = detail_html

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        meta.title_jp = re.sub(
            r'\\s*[-–|]\\s*Lulubar.*$', '', meta.title_jp, flags=re.IGNORECASE
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
            r'<img[^>]*class="[^"]*cover[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*id="[^"]*video_cover[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    if not meta.cover_url:
        images = re.findall(
            r'<img[^>]*src="([^"]+\\.(?:jpg|jpeg|png|webp))"',
            html, re.IGNORECASE
        )
        for img in images:
            if 'logo' not in img.lower() and 'icon' not in img.lower():
                meta.cover_url = img.strip()
                meta.poster_url = meta.cover_url
                break

    return meta

"""Madouqu scraper (madouqu.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://madouqu.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from Madouqu."""
    num = number.upper()

    # Search
    search_url = f"{BASE_URL}/?s={num.lower()}"
    html = fetch_text(search_url)
    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="madouqu",
        image_cut="right",
    )

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    # Find first result link
    match = re.search(
        r'<a\\s+href="([^"]+)"[^>]*title="[^"]*' + re.escape(num) + r'[^"]*"',
        html, re.IGNORECASE
    )
    if not match:
        match = re.search(
            r'<a\\s+href="([^"]+)"[^>]*>([^<]*' + re.escape(num) + r'[^<]*)</a>',
            html, re.IGNORECASE
        )

    if match:
        href = match.group(1)
        if href.startswith("/"):
            href = BASE_URL + href
        detail_html = fetch_text(href)
        if detail_html:
            html = detail_html

            # Better title from detail
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
            r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*attachment-[^"]*"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Date
    date_match = re.search(
        r'<span[^>]*class="[^"]*date[^"]*"[^>]*>([^<]+)',
        html, re.IGNORECASE
    )
    if date_match:
        meta.release = date_match.group(1).strip()

    # Return None if no data was actually scraped
    if not meta.title_jp and not meta.cover_url:
        return None
    return meta

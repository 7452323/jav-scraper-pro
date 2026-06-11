"""Fantastica VR scraper (fantastica-vr.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "http://fantastica-vr.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from Fantastica VR."""
    num = number.upper()

    # Search
    search_url = f"{BASE_URL}/items/search?q={num}"
    html = fetch_text(search_url)
    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="fantastica",
        image_cut="right",
    )

    # Title from search results
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    # Find first result link
    match = re.search(
        r'<a\\s+href="(/items/detail/[^"]+)"',
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
            dt = re.search(
                r'<h1[^>]*>\\s*([^<]+)\\s*</h1>', html, re.IGNORECASE
            )
            if dt:
                t = dt.group(1).strip()
                if t and len(t) > 3:
                    meta.title_jp = t

    # Cover
    cover_match = re.search(
        r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*main-image[^"]*"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*id="[^"]*item_img[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    if not meta.cover_url:
        # Try finding any reasonable image
        images = re.findall(
            r'<img[^>]*src="([^"]+\\.(?:jpg|jpeg|png|webp))"',
            html, re.IGNORECASE
        )
        for img in images:
            if 'logo' not in img.lower() and 'icon' not in img.lower() and 'banner' not in img.lower():
                meta.cover_url = img.strip()
                meta.poster_url = meta.cover_url
                break

    # Return None if no data was actually scraped
    if not meta.title_jp and not meta.cover_url:
        return None
    return meta

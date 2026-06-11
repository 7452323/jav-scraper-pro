"""CNMDB scraper (cnmdb.net)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://cnmdb.net"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from CNMDB."""
    num = number.upper()

    # Search
    search_url = f"{BASE_URL}/s0?q={num}"
    html = fetch_text(search_url)
    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="cnmdb",
        image_cut="right",
    )

    # Find result link
    match = re.search(
        r'<a\\s+href="([^"]+)"[^>]*class="[^"]*search-result[^"]*"',
        html, re.IGNORECASE
    )
    if not match:
        match = re.search(
            r'<a\\s+href="([^"]+)"[^>]*>([^<]*' + re.escape(num) + r'[^<]*)</a>',
            html, re.IGNORECASE
        )

    # Even if we find no link, search page may have result data directly
    # Title from search results
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    # Try to get title from result items
    result_title = re.search(
        r'class="[^"]*title[^"]*"[^>]*>([^<]+)',
        html, re.IGNORECASE
    )
    if result_title:
        t = result_title.group(1).strip()
        if t and len(t) > 3:
            meta.title_jp = t

    # Cover from search results
    cover_match = re.search(
        r'<img[^>]*class="[^"]*thumbnail[^"]*"[^>]*src="([^"]+)"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*src="([^"]+)"[^>]*alt="[^"]*' + re.escape(num) + r'[^"]*"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Follow result link if found
    if match:
        href = match.group(1)
        if href.startswith("/"):
            href = BASE_URL + href
        detail_html = fetch_text(href)
        if detail_html:
            # Better title from detail page
            dt = re.search(
                r'<title>\\s*(.*?)\\s*</title>', detail_html, re.IGNORECASE | re.DOTALL
            )
            if dt:
                meta.title_jp = dt.group(1).strip()

            # Better cover
            dc = re.search(
                r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
                detail_html, re.IGNORECASE
            )
            if dc:
                meta.cover_url = dc.group(1).strip()
                meta.poster_url = meta.cover_url

    return meta

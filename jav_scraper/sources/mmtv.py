"""MMTV scraper (7mmtv.sx)."""

import re
import urllib.parse

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://www.7mmtv.sx"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from MMTV."""
    num = number.upper()

    # Search
    search_url = f"{BASE_URL}/zh/searchform_search/all/index.html?search={urllib.parse.quote(num)}"
    html = fetch_text(search_url)
    if not html:
        # Try alternative URL pattern
        search_url = f"{BASE_URL}/searchform_search/all/index.html?search={urllib.parse.quote(num)}"
        html = fetch_text(search_url)
        if not html:
            return None

    meta = JavMetadata(
        number=num,
        source="mmtv",
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
            r'<a\\s+href="([^"]*video[^"]*)"[^>]*>\\s*<img[^>]*src="[^"]+"[^>]*alt="[^"]*' +
            re.escape(num) + r'[^"]*"',
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
            r'\\s*[-–|]\\s*MMTV.*$', '', meta.title_jp, flags=re.IGNORECASE
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
            r'<img[^>]*class="[^"]*video-cover[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*id="[^"]*cover[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Actors
    actor_text = re.search(
        r'(?:主演|出演|女優)[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if actor_text:
        names = re.split(r'[、,，/]', actor_text.group(1).strip())
        for name in names:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    if not meta.actors:
        actor_links = re.findall(
            r'<a[^>]*href="/zh/star/[^"]+"[^>]*>([^<]+)</a>',
            html, re.IGNORECASE
        )
        for name in actor_links:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # Release date
    date_match = re.search(
        r'(\\d{4}[/-]\\d{2}[/-]\\d{2})', html
    )
    if date_match:
        meta.release = date_match.group(1).strip().replace("/", "-")

    # Return None if no data was actually scraped
    if not meta.title_jp and not meta.cover_url:
        return None
    return meta

"""HSCangku scraper (hsck860.cc)."""

import re
import urllib.parse

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "http://hsck860.cc"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from HSCangku."""
    num = number.upper()

    # Try various search URL patterns
    search_urls = [
        f"{BASE_URL}/vodsearch/-------------.html?wd={urllib.parse.quote(num)}",
        f"{BASE_URL}/vodsearch.html?wd={urllib.parse.quote(num)}",
        f"{BASE_URL}/search/-------------.html?wd={urllib.parse.quote(num)}",
    ]

    html = ""
    for url in search_urls:
        html = fetch_text(url)
        if html:
            break

    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="hscangku",
        image_cut="right",
    )

    # Title from search page
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    # Find first result link
    match = re.search(
        r'<a\\s+href="(/voddetail/[^"]+)"',
        html, re.IGNORECASE
    )
    if not match:
        match = re.search(
            r'<a\\s+href="(/vod/[^"]+)"',
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
            r'<img[^>]*class="[^"]*vod-img[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*id="[^"]*pic[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Actors
    actor_text = re.search(
        r'主演[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if actor_text:
        names = re.split(r'[、,，/]', actor_text.group(1).strip())
        for name in names:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    if not meta.actors:
        actor_links = re.findall(
            r'<a[^>]*href="[^"]*star[^"]*"[^>]*>([^<]+)</a>',
            html, re.IGNORECASE
        )
        for name in actor_links:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # Release year
    year_match = re.search(
        r'年份[：:]\\s*(\\d{4})', html, re.IGNORECASE
    )
    if year_match:
        meta.release = year_match.group(1).strip()

    # Director
    dir_match = re.search(
        r'导演[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if dir_match:
        meta.director = dir_match.group(1).strip()

    # Return None if no data was actually scraped
    if not meta.title_jp and not meta.cover_url:
        return None
    return meta

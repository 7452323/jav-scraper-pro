"""Giga scraper (giga-web.jp)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://www.giga-web.jp"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from Giga."""
    num = number.upper()

    # Searching via product list
    search_url = f"{BASE_URL}/product/list.php?q={num}"
    html = fetch_text(search_url)
    if not html:
        # Try different path
        search_url = f"{BASE_URL}/products/list.php?keyword={num}"
        html = fetch_text(search_url)
        if not html:
            return None

    meta = JavMetadata(
        number=num,
        source="giga",
        image_cut="right",
    )

    # Find first result link
    match = re.search(
        r'<a\\s+href="(/product/detail/[^"]+)"',
        html, re.IGNORECASE
    )
    if not match:
        match = re.search(
            r'<a\\s+href="(/products/detail/[^"]+)"',
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
            r'\\s*[-–|]\\s*GIGA.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    # Better title from product name
    prod_match = re.search(
        r'<h2[^>]*>\\s*([^<]+)\\s*</h2>', html, re.IGNORECASE
    )
    if prod_match:
        t = prod_match.group(1).strip()
        if t and len(t) > 3:
            meta.title_jp = t

    # Cover
    cover_match = re.search(
        r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*class="[^"]*main-image[^"]*"[^>]*src="([^"]+)"',
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

    # Actors
    actor_links = re.findall(
        r'<a[^>]*href="/[^"]*actress[^"]*"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    for name in actor_links:
        name = name.strip()
        if name:
            meta.actors.append(Actor(name=name, role="actor"))

    if not meta.actors:
        actor_text = re.search(
            r'出演[：:]\\s*([^<]+)', html, re.IGNORECASE
        )
        if actor_text:
            names = re.split(r'[、,，/]', actor_text.group(1).strip())
            for name in names:
                name = name.strip()
                if name:
                    meta.actors.append(Actor(name=name, role="actor"))

    return meta

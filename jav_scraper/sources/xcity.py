"""XCity scraper (xcity.jp)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://xcity.jp"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from XCity."""
    num = number.upper()

    # Search
    search_url = f"{BASE_URL}/result_published/?q={num}"
    html = fetch_text(search_url)
    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="xcity",
        image_cut="right",
    )

    # Find detail page link
    match = re.search(
        r'<a\\s+href="(/[^"]+)"[^>]*>\\s*<img[^>]*alt="[^"]*' +
        re.escape(num) + r'[^"]*"',
        html, re.IGNORECASE
    )
    if not match:
        match = re.search(
            r'<a\\s+href="(/detail/[^"]+)"',
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
            r'\\s*[-–|]\\s*XCity.*$', '', meta.title_jp, flags=re.IGNORECASE
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
            r'<img[^>]*class="[^"]*package[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Actors
    actor_links = re.findall(
        r'<a[^>]*href="/idol/[^"]+"[^>]*>([^<]+)</a>',
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

    # Release date
    date_match = re.search(
        r'(\\d{4}[/-]\\d{2}[/-]\\d{2})', html
    )
    if date_match:
        meta.release = date_match.group(1).strip().replace("/", "-")

    # Tags
    tags = re.findall(
        r'<a[^>]*href="/genre/[^"]+"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    # Return None if no data was actually scraped
    if not meta.title_jp and not meta.cover_url:
        return None
    return meta

"""FreeJAVBT scraper (freejavbt.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://freejavbt.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from FreeJAVBT."""
    num = number.upper()

    # Try direct page
    url = f"{BASE_URL}/{num}"
    html = fetch_text(url)
    if not html:
        url = f"{BASE_URL}/{num.lower()}"
        html = fetch_text(url)
        if not html:
            url = f"{BASE_URL}/{num.replace('-', '')}"
            html = fetch_text(url)
            if not html:
                return None

    meta = JavMetadata(
        number=num,
        source="freejavbt",
        image_cut="right",
    )

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        meta.title_jp = re.sub(
            r'\\s*[-–|]\\s*FreeJAVBT.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    # Better title
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
            r'<img[^>]*class="[^"]*product-image[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'class="[^"]*poster[^"]*"[^>]*>\\s*<img[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Release date
    date_match = re.search(
        r'(\\d{4}[/-]\\d{2}[/-]\\d{2})', html
    )
    if date_match:
        meta.release = date_match.group(1).strip().replace("/", "-")

    # Actors
    actor_text = re.search(
        r'(?:出演|女優|cast)[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if actor_text:
        names = re.split(r'[、,，/]', actor_text.group(1).strip())
        for name in names:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    return meta

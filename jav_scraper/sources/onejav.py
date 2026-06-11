"""OneJAV scraper (onejav.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://onejav.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from OneJAV."""
    url = f"{BASE_URL}/search/{number.lower()}/"
    html = fetch_text(url)
    if not html:
        return None

    # Find the first result link
    match = re.search(
        r'<a\s+href="(/movie/[^"]+)"[^>]*>',
        html,
        re.IGNORECASE,
    )
    if not match:
        return None

    movie_url = BASE_URL + match.group(1)
    html = fetch_text(movie_url)
    if not html:
        return None

    meta = JavMetadata(
        number=number.upper(),
        source="onejav",
        mosaic="Censored",
    )

    # Title
    title_match = re.search(
        r'<title>\s*(.*?)\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    # Actors
    actor_matches = re.findall(
        r'<a\s+href="/actor/[^"]+"[^>]*>([^<]+)</a>',
        html,
        re.IGNORECASE,
    )
    for name in actor_matches:
        meta.actors.append(Actor(name=name.strip(), role="actor"))

    # Date
    date_match = re.search(
        r'<strong>Date:</strong>\s*([^<\s]+)', html, re.IGNORECASE
    )
    if date_match:
        meta.release = date_match.group(1).strip()

    # Runtime
    runtime_match = re.search(
        r'<strong>Duration:</strong>\s*(\d+)', html, re.IGNORECASE
    )
    if runtime_match:
        meta.runtime = runtime_match.group(1).strip()

    # Tags
    tags = re.findall(
        r'<a\s+href="/tag/[^"]+"[^>]*>([^<]+)</a>',
        html,
        re.IGNORECASE,
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    # Cover image
    cover_match = re.search(
        r'<img\s+[^>]*src="([^"]+)"[^>]*class="[^"]*hw-image[^"]*"',
        html,
        re.IGNORECASE,
    )
    if not cover_match:
        cover_match = re.search(
            r'<img\s+[^>]*class="[^"]*hw-image[^"]*"[^>]*src="([^"]+)"',
            html,
            re.IGNORECASE,
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()

    # Poster
    if meta.cover_url:
        meta.poster_url = meta.cover_url

    return meta

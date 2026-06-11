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

    # Find the best matching result link (prefer exact match over first)
    all_links = re.findall(
        r'<a\s+href="(/(?:movie|torrent)/[^"]+)"[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )

    best_match = None
    num_lower = number.lower().replace("-", "")
    for link_href, link_text in all_links:
        link_clean = link_text.strip().lower().replace("-", "")
        # Exact match (without hyphens) — perfect
        if link_clean == num_lower:
            best_match = link_href
            break
        # Partial match — use if no perfect found
        if num_lower in link_href.lower() and not best_match:
            best_match = link_href

    if not best_match:
        return None

    movie_url = BASE_URL + best_match
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
        # Clean " - OneJAV.com - Free JAV Torrents" suffix
        meta.title_jp = re.sub(
            r'\s*[-–|]\s*OneJAV\..*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

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

    # Cover image — try multiple patterns (class may come before or after src)
    cover_match = re.search(
        r'<img[^>]*class="[^"]*image[^"]*"[^>]*src="([^"]+\.(?:jpg|jpeg|png)(?:\?[^"]*)?)"',
        html,
        re.IGNORECASE,
    )
    if not cover_match:
        cover_match = re.search(
            r'<img\s+[^>]*class="[^"]*hw-image[^"]*"[^>]*src="([^"]+)"',
            html,
            re.IGNORECASE,
        )
    if not cover_match:
        cover_match = re.search(
            r'<img\s+[^>]*src="([^"]+)"[^>]*class="[^"]*hw-image[^"]*"',
            html,
            re.IGNORECASE,
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        # Skip static/internal images
        if "static" in meta.cover_url or meta.cover_url.startswith("/"):
            meta.cover_url = None

    # Poster
    if meta.cover_url:
        meta.poster_url = meta.cover_url

    return meta

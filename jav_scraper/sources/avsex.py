"""AVSEX scraper (avsex.com / avsex.xyz)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

DOMAINS = [
    "https://avsex.com",
    "https://avsex.xyz",
]


def _try_fetch(path: str) -> str:
    """Try fetching from multiple domains."""
    for domain in DOMAINS:
        html = fetch_text(domain + path)
        if html:
            return html
    return ""


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from AVSEX."""
    num = number.upper()

    # Try direct page
    html = _try_fetch(f"/movie/{num}/")
    if not html:
        html = _try_fetch(f"/{num}/")
    if not html:
        # Try search
        search_html = _try_fetch(f"/search/{num}/")
        if not search_html:
            return None

        # Find first result
        match = re.search(
            r'<a\s+href="(/[^"]+)"[^>]*>\s*<img[^>]*alt="[^"]*' +
            re.escape(num) +
            r'[^"]*"',
            search_html,
            re.IGNORECASE,
        )
        if not match:
            match = re.search(
                r'<a\s+href="(/movie/[^"]+)"', search_html, re.IGNORECASE
            )
        if not match:
            return None

        path = match.group(1)
        html = _try_fetch(path)
        if not html:
            return None

    meta = JavMetadata(
        number=num,
        source="avsex",
    )

    # Title
    title_match = re.search(
        r'<title>\s*(.*?)\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        meta.title_jp = re.sub(
            r'\s*[-–|]\s*AVSEX.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    # Also try h1
    h1_match = re.search(
        r'<h1[^>]*>\s*([^<]+)\s*</h1>',
        html,
        re.IGNORECASE,
    )
    if h1_match:
        t = h1_match.group(1).strip()
        if t and len(t) > len(num):
            meta.title_jp = t

    # Actors
    actor_links = re.findall(
        r'<a\s+href="/star/[^"]+"[^>]*>\s*([^<\n]+)\s*</a>',
        html,
        re.IGNORECASE,
    )
    for name in actor_links:
        name = name.strip()
        if name:
            meta.actors.append(Actor(name=name, role="actor"))

    # Director
    dir_match = re.search(
        r'監督[：:]\s*([^<\n]+)', html, re.IGNORECASE
    )
    if dir_match:
        meta.director = dir_match.group(1).strip()

    # Release date
    date_match = re.search(
        r'発売日[：:]\s*([^<\s]+)', html, re.IGNORECASE
    )
    if not date_match:
        date_match = re.search(
            r'<strong>発売日[：:]\s*</strong>\s*([^<\s]+)',
            html,
            re.IGNORECASE,
        )
    if date_match:
        meta.release = date_match.group(1).strip()

    # Runtime
    runtime_match = re.search(
        r'収録時間[：:]\s*(\d+)', html, re.IGNORECASE
    )
    if not runtime_match:
        runtime_match = re.search(
            r'<strong>収録時間[：:]\s*</strong>\s*(\d+)',
            html,
            re.IGNORECASE,
        )
    if runtime_match:
        meta.runtime = runtime_match.group(1).strip()

    # Studio / Maker
    maker_match = re.search(
        r'メーカー[：:]\s*([^<\n]+)', html, re.IGNORECASE
    )
    if maker_match:
        meta.studio = maker_match.group(1).strip()
        meta.maker = meta.studio

    publisher_match = re.search(
        r'レーベル[：:]\s*([^<\n]+)', html, re.IGNORECASE
    )
    if publisher_match:
        meta.publisher = publisher_match.group(1).strip()

    # Series
    series_match = re.search(
        r'シリーズ[：:]\s*([^<\n]+)', html, re.IGNORECASE
    )
    if series_match:
        meta.series = series_match.group(1).strip()

    # Genres
    genres = re.findall(
        r'<a\s+href="/genre/[^"]+"[^>]*>([^<]+)</a>',
        html,
        re.IGNORECASE,
    )
    meta.tags = [g.strip() for g in genres if g.strip()]

    # Cover image
    cover_match = re.search(
        r'<a\s+class="bigImage"[^>]*href="([^"]+)"',
        html,
        re.IGNORECASE,
    )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
    else:
        cover_match = re.search(
            r'<img\s+[^>]*class="[^"]*video-cover[^"]*"[^>]*src="([^"]+)"',
            html,
            re.IGNORECASE,
        )
        if cover_match:
            meta.cover_url = cover_match.group(1).strip()

    if meta.cover_url:
        meta.poster_url = meta.cover_url

    # Sample images
    samples = re.findall(
        r'<a\s+href="([^"]+)"[^>]*class="[^"]*sample-box[^"]*"',
        html,
        re.IGNORECASE,
    )
    meta.extrafanart = [s.strip() for s in samples if s.strip()]

    # Score
    score_match = re.search(
        r'評価[：:]\s*([\d.]+)', html, re.IGNORECASE
    )
    if score_match:
        meta.score = score_match.group(1).strip()

    return meta

"""JavDB scraper (javdb.com)."""

import re
import urllib.parse

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://javdb.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from JavDB."""
    # Search for the number
    search_url = f"{BASE_URL}/search?q={urllib.parse.quote(number)}&f=all"
    html = fetch_text(search_url)
    if not html:
        return None

    # Try to find a direct result link
    # Look for links containing the number
    pattern = re.escape(number.upper()) + r'[^<]*</a>'
    match = re.search(
        r'<a\s+href="(' + re.escape(BASE_URL) + r'/v/[^"]+)"[^>]*>',
        html,
        re.IGNORECASE,
    )
    if not match:
        # Try alternative pattern
        match = re.search(
            r'href="(/v/[^"]+)"[^>]*>[^<]*' + re.escape(number.upper()),
            html,
            re.IGNORECASE,
        )

    if not match:
        return None

    href = match.group(1)
    if href.startswith("/"):
        movie_url = BASE_URL + href
    else:
        movie_url = href

    html = fetch_text(movie_url)
    if not html:
        return None

    meta = JavMetadata(
        number=number.upper(),
        source="javdb",
    )

    # Title
    title_match = re.search(
        r'<title>\s*(.*?)\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        # Remove common suffix
        meta.title_jp = re.sub(r'\s*[-–|]\s*JavDB.*$', '', meta.title_jp, flags=re.IGNORECASE).strip()

    # Japanese title (second title block)
    cn_match = re.search(
        r'<div[^>]*class="[^"]*title[^"]*"[^>]*>\s*<h2[^>]*>\s*<strong>([^<]+)',
        html,
        re.IGNORECASE,
    )
    if cn_match:
        meta.title_cn = cn_match.group(1).strip()

    # Actors
    actor_links = re.findall(
        r'<a\s+href="/actors/[^"]+"[^>]*>([^<]+)</a>',
        html,
        re.IGNORECASE,
    )
    for name in actor_links:
        meta.actors.append(Actor(name=name.strip(), role="actor"))

    # Director
    dir_match = re.search(
        r'导演[^<]*<[^>]*>\s*([^<\n]+)',
        html,
        re.IGNORECASE,
    )
    if not dir_match:
        dir_match = re.search(
            r'<strong>导演</strong>\s*[：:]\s*([^<\n]+)',
            html,
            re.IGNORECASE,
        )
    if dir_match:
        meta.director = dir_match.group(1).strip()

    # Release date
    date_match = re.search(
        r'日期[^<]*<[^>]*>\s*([^<\s]+)',
        html,
        re.IGNORECASE,
    )
    if not date_match:
        date_match = re.search(
            r'<strong>日期</strong>\s*[：:]\s*([^<\s]+)',
            html,
            re.IGNORECASE,
        )
    if date_match:
        meta.release = date_match.group(1).strip()

    # Runtime
    runtime_match = re.search(
        r'时长[^<]*<[^>]*>\s*(\d+)',
        html,
        re.IGNORECASE,
    )
    if not runtime_match:
        runtime_match = re.search(
            r'<strong>时长</strong>\s*[：:]\s*(\d+)',
            html,
            re.IGNORECASE,
        )
    if runtime_match:
        meta.runtime = runtime_match.group(1).strip()

    # Studio / Maker
    studio_match = re.search(
        r'片商[^<]*<[^>]*>\s*([^<\n]+)',
        html,
        re.IGNORECASE,
    )
    if studio_match:
        meta.studio = studio_match.group(1).strip()
        meta.maker = meta.studio

    # Series
    series_match = re.search(
        r'系列[^<]*<[^>]*>\s*([^<\n]+)',
        html,
        re.IGNORECASE,
    )
    if series_match:
        meta.series = series_match.group(1).strip()

    # Score
    score_match = re.search(
        r'<span\s+class="[^"]*score-number[^"]*"[^>]*>\s*([\d.]+)',
        html,
        re.IGNORECASE,
    )
    if score_match:
        meta.score = score_match.group(1).strip()

    # Tags / Genres
    tags = re.findall(
        r'<a\s+href="/tags/[^"]+"[^>]*>([^<]+)</a>',
        html,
        re.IGNORECASE,
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    # Cover image
    cover_match = re.search(
        r'<img\s+[^>]*class="[^"]*video-cover[^"]*"[^>]*src="([^"]+)"',
        html,
        re.IGNORECASE,
    )
    if not cover_match:
        cover_match = re.search(
            r'<img\s+[^>]*id="video_cover"[^>]*src="([^"]+)"',
            html,
            re.IGNORECASE,
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    return meta

"""JavBus scraper (javbus.com / javbus.org)."""

import re
import urllib.parse

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

# Try multiple domains
DOMAINS = [
    "https://www.javbus.com",
    "https://www.javbus.org",
]


def _try_domains(path: str) -> str:
    """Try fetching from multiple domains, return first success."""
    for domain in DOMAINS:
        html = fetch_text(domain + path)
        if html:
            return html
    return ""


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from JavBus."""
    num = number.upper()

    # Try direct page first (most JavBus URLs use the number as path)
    html = _try_domains(f"/{num}")
    if not html:
        # Try search
        search_path = f"/search/{urllib.parse.quote(num)}&type=all"
        html = _try_domains(search_path)
        if not html:
            return None

    # Check for age verification / blocked pages
    if re.search(r'age.?verification|please.?verify|Access Denied|Just a moment|challenge-platform', html, re.IGNORECASE):
        return None

    # First, check if the initial direct page had a real movie-box (indicating search results)
    # If we went to /FNS-151 directly and got a search results page
    movie_link_match = re.search(
        r'<a\s+class="movie-box"[^>]*href="([^"]+)"',
        html,
        re.IGNORECASE,
    )

    if movie_link_match:
        # We got search results instead of a direct page
        movie_url = movie_link_match.group(1)
        if movie_url.startswith("/"):
            movie_url = DOMAINS[0] + movie_url
        html = fetch_text(movie_url)
        if not html:
            return None
    # If no movie-box link found, maybe we hit the actual page directly
    # Check if this is actually a product page (has known JavBus fields)
    elif not re.search(r'发行时间|制作商|star/', html, re.IGNORECASE):
        # Not a real JavBus product page
        return None

    meta = JavMetadata(
        number=num,
        source="javbus",
        mosaic="Censored",
    )

    # Title
    title_match = re.search(
        r'<title>\s*(.*?)\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        # Clean JavBus suffix
        meta.title_jp = re.sub(
            r'\s*[-–|]\s*JavBus.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()
        meta.title_jp = re.sub(
            r'\s*[-–|]\s*JavDB.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    # Also look for the big title
    big_title_match = re.search(
        r'<div[^>]*class="[^"]*container[^"]*"[^>]*>.*?<h3[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if big_title_match:
        t = big_title_match.group(1).strip()
        if t and len(t) > len(num):
            meta.title_jp = t

    # Actors - JavBus uses star links
    star_links = re.findall(
        r'<a\s+href="[^"]*star/[^"]+"[^>]*>\s*([^<\n]+)\s*</a>',
        html,
        re.IGNORECASE,
    )
    for name in star_links:
        name = name.strip()
        if name:
            meta.actors.append(Actor(name=name, role="actor"))

    # Also check for actress spans
    actress_spans = re.findall(
        r'<span>[^<]*actress[^<]*</span>\s*<span[^>]*>\s*([^<\n]+)\s*</span>',
        html,
        re.IGNORECASE,
    )
    for name in actress_spans:
        name = name.strip()
        if name and not any(a.name == name for a in meta.actors):
            meta.actors.append(Actor(name=name, role="actor"))

    # Director
    dir_match = re.search(
        r'<span>导演[：:]?\s*</span>\s*<span[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    if dir_match:
        meta.director = dir_match.group(1).strip()

    # Release date
    date_match = re.search(
        r'<span>发行时间[：:]?\s*</span>\s*<span[^>]*>\s*([^<\s]+)',
        html,
        re.IGNORECASE,
    )
    if date_match:
        meta.release = date_match.group(1).strip()

    # Runtime
    runtime_match = re.search(
        r'<span>长度[：:]?\s*</span>\s*<span[^>]*>\s*(\d+)',
        html,
        re.IGNORECASE,
    )
    if runtime_match:
        meta.runtime = runtime_match.group(1).strip()

    # Studio / Maker
    studio_match = re.search(
        r'<span>制作商[：:]?\s*</span>\s*<span[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    if studio_match:
        meta.studio = studio_match.group(1).strip()

    maker_match = re.search(
        r'<span>发行商[：:]?\s*</span>\s*<span[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    if maker_match:
        meta.maker = maker_match.group(1).strip()

    # Series
    series_match = re.search(
        r'<span>系列[：:]?\s*</span>\s*<span[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    if series_match:
        meta.series = series_match.group(1).strip()

    # Genre / Tags
    genres = re.findall(
        r'<a\s+href="[^"]*genre/[^"]+"[^>]*>\s*<span[^>]*>\s*([^<]+)',
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
            r'<img\s+[^>]*class="[^"]*bigImage[^"]*"[^>]*src="([^"]+)"',
            html,
            re.IGNORECASE,
        )
        if cover_match:
            meta.cover_url = cover_match.group(1).strip()

    if meta.cover_url:
        meta.poster_url = meta.cover_url

    # Sample images (extrafanart)
    samples = re.findall(
        r'<a\s+href="([^"]+)"[^>]*class="[^"]*sample-box[^"]*"',
        html,
        re.IGNORECASE,
    )
    meta.extrafanart = [s.strip() for s in samples if s.strip()]

    # Mosaic type
    if re.search(r'无码|uncensored|無碼', html, re.IGNORECASE):
        meta.mosaic = "Uncensored"

    return meta

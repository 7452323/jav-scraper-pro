"""AVSOX scraper (avsox.host / avsox.click)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

DOMAINS = [
    "https://avsox.host",
    "https://avsox.click",
    "https://www.avsox.host",
]


def _try_fetch(path: str) -> str:
    """Try fetching from multiple domains."""
    for domain in DOMAINS:
        html = fetch_text(domain + path)
        if html:
            return html
    return ""


def _is_valid_page(html: str) -> bool:
    """Check if the page contains actual JAV content vs redirect/survey."""
    # Block known fake pages
    blocklist = [
        'Loading...', 'survey-smiles', 'Just a moment',
        'age.verification', 'Access Denied', 'challenge-platform',
    ]
    for b in blocklist:
        if re.search(b, html, re.IGNORECASE):
            return False
    # Must have at least some JAV metadata markers
    has_content = bool(re.search(
        r'発売日|メーカー|star/|genre/|sample-box', html, re.IGNORECASE
    ))
    if not has_content:
        return False
    return True


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from AVSOX."""
    num = number.upper()

    # Try direct page
    html = _try_fetch(f"/{num}/")
    if not html:
        # Try search
        search_html = _try_fetch(f"/search/{num}/")
        if not search_html:
            return None
        html = search_html

        # Find first result link
        match = re.search(
            r'<a\s+href="(/[^"]+/[^"]+)"[^>]*>\s*<div[^>]*class="[^"]*photo-frame[^"]*"',
            html,
            re.IGNORECASE,
        )
        if not match:
            match = re.search(
                r'<a\s+href="(/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+)"[^>]*>',
                html,
                re.IGNORECASE,
            )
            if not match:
                return None

        path = match.group(1)
        html = _try_fetch(path if path.startswith("/") else f"/{path}")
        if not html:
            return None

    # Validate page content
    if not _is_valid_page(html):
        return None

    meta = JavMetadata(
        number=num,
        source="avsox",
    )

    # Title
    title_match = re.search(
        r'<h3[^>]*>\s*([^<]+)\s*</h3>',
        html,
        re.IGNORECASE,
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    if not meta.title_jp:
        title_match = re.search(
            r'<title>\s*(.*?)\s*</title>', html, re.IGNORECASE | re.DOTALL
        )
        if title_match:
            meta.title_jp = title_match.group(1).strip()
            meta.title_jp = re.sub(
                r'\s*[-–|]\s*AVSOX.*$', '', meta.title_jp, flags=re.IGNORECASE
            ).strip()

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

    # Also check for actress list
    if not meta.actors:
        actor_spans = re.findall(
            r'<span\s+class="[^"]*star[^"]*"[^>]*>\s*([^<]+)\s*</span>',
            html,
            re.IGNORECASE,
        )
        for name in actor_spans:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # Director
    dir_match = re.search(
        r'監督[：:]\s*([^<\n]+)', html, re.IGNORECASE
    )
    if dir_match:
        meta.director = dir_match.group(1).strip()
    else:
        dir_match = re.search(
            r'<strong>監督[：:]\s*</strong>\s*([^<]+)',
            html,
            re.IGNORECASE,
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
    studio_match = re.search(
        r'メーカー[：:]\s*([^<\n]+)', html, re.IGNORECASE
    )
    if not studio_match:
        studio_match = re.search(
            r'<strong>メーカー[：:]\s*</strong>\s*([^<]+)',
            html,
            re.IGNORECASE,
        )
    if studio_match:
        meta.studio = studio_match.group(1).strip()
        meta.maker = meta.studio

    # Series
    series_match = re.search(
        r'シリーズ[：:]\s*([^<\n]+)', html, re.IGNORECASE
    )
    if not series_match:
        series_match = re.search(
            r'<strong>シリーズ[：:]\s*</strong>\s*([^<]+)',
            html,
            re.IGNORECASE,
        )
    if series_match:
        meta.series = series_match.group(1).strip()

    # Genres / Tags
    genres = re.findall(
        r'<a\s+href="/genre/[^"]+"[^>]*>\s*<span[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    if not genres:
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
            r'<img\s+[^>]*class="[^"]*bigImage[^"]*"[^>]*src="([^"]+)"',
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

    # Score / Rating
    score_match = re.search(
        r'<strong>評価[：:]\s*</strong>\s*([\d.]+)',
        html,
        re.IGNORECASE,
    )
    if score_match:
        meta.score = score_match.group(1).strip()

    # Description / Plot
    desc_match = re.search(
        r'<div[^>]*class="[^"]*description[^"]*"[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if desc_match:
        meta.plot = desc_match.group(1).strip()
        meta.plot = re.sub(r'<[^>]+>', '', meta.plot)

    return meta

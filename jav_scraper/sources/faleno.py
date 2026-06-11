"""FALENO official site scraper (faleno.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://faleno.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from FALENO official site."""
    num = number.upper()

    # Try direct product page
    url = f"{BASE_URL}/products/{num.lower()}/"
    html = fetch_text(url)
    if not html:
        # Try without trailing slash
        url = f"{BASE_URL}/products/{num.lower()}"
        html = fetch_text(url)
        if not html:
            # Try search
            search_url = f"{BASE_URL}/products/?s={num.lower()}"
            html = fetch_text(search_url)
            if not html:
                return None

            # Find first result link
            match = re.search(
                r'<a\s+href="([^"]+)"[^>]*>\s*<img[^>]*alt="[^"]*' +
                re.escape(num) +
                r'[^"]*"',
                html,
                re.IGNORECASE,
            )
            if not match:
                match = re.search(
                    r'<a\s+href="(/products/[^"]+)"',
                    html,
                    re.IGNORECASE,
                )
            if not match:
                return None

            href = match.group(1)
            if href.startswith("/"):
                product_url = BASE_URL + href
            else:
                product_url = href
            html = fetch_text(product_url)
            if not html:
                return None

    meta = JavMetadata(
        number=num,
        source="faleno",
        studio="FALENO",
        maker="FALENO",
        mosaic="Censored",
    )

    # Title
    title_match = re.search(
        r'<title>\s*(.*?)\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        # Remove site name suffix
        meta.title_jp = re.sub(
            r'\s*[|–-]\s*FALENO.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    # Product title (often in h1 or h2)
    h1_match = re.search(
        r'<h1[^>]*>\s*([^<]+)\s*</h1>',
        html,
        re.IGNORECASE,
    )
    if h1_match:
        t = h1_match.group(1).strip()
        if t and len(t) > 3:
            meta.title_jp = t

    # Check for product-item-title class
    item_match = re.search(
        r'class="[^"]*product-item-title[^"]*"[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    if item_match:
        t = item_match.group(1).strip()
        if t and len(t) > 3:
            meta.title_jp = t

    # Actors - look for actress names in the product page
    # FALENO often lists actresses as links or text
    actress_patterns = [
        r'出演者[：:]\s*([^<]+)',
        r'主演[：:]\s*([^<]+)',
        r'cast[：:]\s*([^<]+)',
        r'Actress[：:]\s*([^<]+)',
    ]
    for pattern in actress_patterns:
        cast_match = re.search(pattern, html, re.IGNORECASE)
        if cast_match:
            cast_text = cast_match.group(1).strip()
            # Split by common delimiters
            names = re.split(r'[、,，/／\s]+', cast_text)
            for name in names:
                name = name.strip()
                if name and len(name) > 0:
                    meta.actors.append(Actor(name=name, role="actor"))
            break

    # Also look for actress links
    if not meta.actors:
        actress_links = re.findall(
            r'<a[^>]*href="/actress/[^"]+"[^>]*>\s*([^<]+)\s*</a>',
            html,
            re.IGNORECASE,
        )
        for name in actress_links:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # Release date
    date_patterns = [
        r'発売日[：:]\s*([^<\s]+)',
        r'配信日[：:]\s*([^<\s]+)',
        r'リリース[：:]\s*([^<\s]+)',
        r'Release[：:]\s*([^<\s]+)',
        r'date[：:]\s*([^<\s]+)',
    ]
    for pattern in date_patterns:
        date_match = re.search(pattern, html, re.IGNORECASE)
        if date_match:
            meta.release = date_match.group(1).strip()
            break

    # Runtime
    runtime_patterns = [
        r'収録時間[：:]\s*(\d+)',
        r'再生時間[：:]\s*(\d+)',
        r'時間[：:]\s*(\d+)\s*分',
        r'Runtime[：:]\s*(\d+)',
        r'mins?[：:]\s*(\d+)',
    ]
    for pattern in runtime_patterns:
        runtime_match = re.search(pattern, html, re.IGNORECASE)
        if runtime_match:
            meta.runtime = runtime_match.group(1).strip()
            break

    # Series
    series_patterns = [
        r'シリーズ[：:]\s*([^<]+)',
        r'Series[：:]\s*([^<]+)',
    ]
    for pattern in series_patterns:
        series_match = re.search(pattern, html, re.IGNORECASE)
        if series_match:
            meta.series = series_match.group(1).strip()
            break

    # Director
    director_patterns = [
        r'監督[：:]\s*([^<]+)',
        r'ディレクター[：:]\s*([^<]+)',
        r'Director[：:]\s*([^<]+)',
    ]
    for pattern in director_patterns:
        dir_match = re.search(pattern, html, re.IGNORECASE)
        if dir_match:
            meta.director = dir_match.group(1).strip()
            break

    # Tags / Genres
    genre_patterns = [
        r'ジャンル[：:]\s*([^<]+)',
        r'タグ[：:]\s*([^<]+)',
        r'Genre[：:]\s*([^<]+)',
    ]
    for pattern in genre_patterns:
        genre_match = re.search(pattern, html, re.IGNORECASE)
        if genre_match:
            genre_text = genre_match.group(1).strip()
            genres = re.split(r'[、,，/／]', genre_text)
            meta.tags = [g.strip() for g in genres if g.strip()]
            break

    # Cover image
    cover_patterns = [
        r'<meta\s+property="og:image"[^>]*content="([^"]+)"',
        r'<img\s+[^>]*class="[^"]*cover-image[^"]*"[^>]*src="([^"]+)"',
        r'<img\s+[^>]*class="[^"]*product-image[^"]*"[^>]*src="([^"]+)"',
        r'<img\s+[^>]*id="[^"]*cover[^"]*"[^>]*src="([^"]+)"',
    ]
    for pattern in cover_patterns:
        cover_match = re.search(pattern, html, re.IGNORECASE)
        if cover_match:
            meta.cover_url = cover_match.group(1).strip()
            meta.poster_url = meta.cover_url
            break

    # Description / Plot
    desc_patterns = [
        r'<meta\s+name="description"[^>]*content="([^"]+)"',
        r'<div[^>]*class="[^"]*description[^"]*"[^>]*>\s*([^<]+)',
        r'<div[^>]*class="[^"]*product-description[^"]*"[^>]*>\s*([^<]+)',
    ]
    for pattern in desc_patterns:
        desc_match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if desc_match:
            desc = desc_match.group(1).strip()
            # Clean HTML tags
            desc = re.sub(r'<[^>]+>', '', desc)
            meta.plot = desc
            break

    return meta

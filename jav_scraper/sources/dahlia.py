"""Dahlia scraper (dahlia-av.jp) — like FALENO format."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://dahlia-av.jp"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from Dahlia AV.

    Dahlia is a FALENO sister brand using similar URL patterns.
    """
    num = number.upper()

    # Try direct product page
    url = f"{BASE_URL}/works/{num}/"
    html = fetch_text(url)
    if not html:
        url = f"{BASE_URL}/works/{num.lower()}/"
        html = fetch_text(url)
        if not html:
            # Try search
            search_url = f"{BASE_URL}/works/?s={num.lower()}"
            html = fetch_text(search_url)
            if not html:
                return None

            # Find first result link
            match = re.search(
                r'<a\\s+href="([^"]+)"[^>]*>\\s*<img[^>]*alt="[^"]*' +
                re.escape(num) + r'[^"]*"',
                html, re.IGNORECASE
            )
            if not match:
                match = re.search(
                    r'<a\\s+href="(/works/[^"]+)"',
                    html, re.IGNORECASE
                )
            if not match:
                return None

            href = match.group(1)
            if href.startswith("/"):
                url = BASE_URL + href
            else:
                url = href
            html = fetch_text(url)
            if not html:
                return None

    meta = JavMetadata(
        number=num,
        source="dahlia",
        studio="Dahlia",
        maker="Dahlia",
        image_cut="right",
    )

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        meta.title_jp = re.sub(
            r'\\s*[-–|]\\s*Dahlia.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    h1_match = re.search(
        r'<h1[^>]*>\\s*([^<]+)\\s*</h1>', html, re.IGNORECASE
    )
    if h1_match:
        t = h1_match.group(1).strip()
        if t and len(t) > 3:
            meta.title_jp = t

    # Actors
    cast_match = re.search(
        r'出演[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if cast_match:
        names = re.split(r'[、,，/]', cast_match.group(1).strip())
        for name in names:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    if not meta.actors:
        actor_links = re.findall(
            r'<a[^>]*href="/actress/[^"]+"[^>]*>([^<]+)</a>',
            html, re.IGNORECASE
        )
        for name in actor_links:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # Cover
    cover_match = re.search(
        r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*class="[^"]*cover[^"]*"[^>]*src="([^"]+)"',
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

    # Runtime
    runtime_match = re.search(
        r'(\\d+)\\s*分', html
    )
    if runtime_match:
        meta.runtime = runtime_match.group(1).strip()

    return meta

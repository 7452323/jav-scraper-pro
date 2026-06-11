"""FC2 PPV DB scraper (fc2ppvdb.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://fc2ppvdb.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from FC2 PPV DB.

    FC2 numbers are numeric or FC2-XXXXX format.
    """
    # Clean number
    num = re.sub(r'[^0-9]', '', number)
    if not num:
        return None

    url = f"{BASE_URL}/articles/{num}"
    html = fetch_text(url)
    if not html:
        url = f"{BASE_URL}/articles/{num}/"
        html = fetch_text(url)
    if not html:
        return None

    meta = JavMetadata(
        number=f"FC2-{num}",
        source="fc2ppvdb",
        image_cut="left",
    )

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        meta.title_jp = re.sub(
            r'\\s*[-–|]\\s*FC2.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    # Better title from h1 or h2
    h1_match = re.search(
        r'<h1[^>]*>\\s*([^<]+)\\s*</h1>', html, re.IGNORECASE
    )
    if h1_match:
        t = h1_match.group(1).strip()
        if t and len(t) > 3:
            meta.title_jp = t

    # Cover image
    cover_match = re.search(
        r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*thumbnail[^"]*"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'id="[^"]*cover[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Actors / cast
    cast_match = re.search(
        r'出演[：:]\\s*([^<]+)', html, re.IGNORECASE
    )
    if cast_match:
        names = re.split(r'[、,，/]', cast_match.group(1).strip())
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

    return meta

"""FC2 scraper (adult.contents.fc2.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://adult.contents.fc2.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from FC2 adult content.

    FC2 numbers are purely numeric.
    """
    # Strip any non-numeric prefix
    num = re.sub(r'^FC2[-\s]*', '', number, flags=re.IGNORECASE)
    num = re.sub(r'[^0-9]', '', num)
    if not num:
        return None

    url = f"{BASE_URL}/article/{num}/"
    html = fetch_text(url)
    if not html:
        url = f"{BASE_URL}/article/{num}"
        html = fetch_text(url)
    if not html:
        return None

    meta = JavMetadata(
        number=f"FC2-{num}",
        source="fc2",
        mosaic="Uncensored",
        image_cut="right",
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

    # Title from h1
    h1_match = re.search(
        r'<h1[^>]*>\\s*([^<]+)\\s*</h1>', html, re.IGNORECASE
    )
    if h1_match:
        t = h1_match.group(1).strip()
        if t:
            meta.title_jp = t

    # Cover image
    cover_match = re.search(
        r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'class="[^"]*detail_package[^"]*"[^>]*>\\s*<img[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*package[^"]*"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Tags
    tags = re.findall(
        r'<a[^>]*href="/article/tag/[^"]+"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    # Release date
    date_match = re.search(
        r'(\\d{4}[/-]\\d{2}[/-]\\d{2})', html
    )
    if date_match:
        meta.release = date_match.group(1).strip().replace("/", "-")

    # Description
    desc_match = re.search(
        r'<meta\\s+name="description"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if desc_match:
        meta.plot = desc_match.group(1).strip()

    if not meta.plot:
        desc_match = re.search(
            r'class="[^"]*detail_text[^"]*"[^>]*>\\s*(.*?)</div>',
            html, re.IGNORECASE | re.DOTALL
        )
        if desc_match:
            desc = desc_match.group(1).strip()
            desc = re.sub(r'<[^>]+>', '', desc)
            desc = re.sub(r'\\s+', ' ', desc).strip()
            meta.plot = desc

    # Return None if no data was actually scraped
    if not meta.title_jp and not meta.cover_url:
        return None
    return meta

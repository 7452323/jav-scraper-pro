"""FC2 Club scraper (fc2club.top)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://fc2club.top"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from FC2 Club.

    FC2 numbers may be in FC2-XXXXX format.
    """
    # Clean number
    num = re.sub(r'[^0-9]', '', number)
    if not num:
        return None

    url = f"{BASE_URL}/html/FC2-{num}.html"
    html = fetch_text(url)
    if not html:
        return None

    meta = JavMetadata(
        number=f"FC2-{num}",
        source="fc2club",
        image_cut="right",
    )

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        # Remove common suffixes
        meta.title_jp = re.sub(
            r'\\s*[-–|]\\s*FC2.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    # Cover image
    cover_match = re.search(
        r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*cover[^"]*"',
            html, re.IGNORECASE
        )
    if not cover_match:
        cover_match = re.search(
            r'<img[^>]*id="[^"]*cover[^"]*"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    if not meta.cover_url:
        # Try any large image
        images = re.findall(
            r'<img[^>]*src="([^"]+\\.(?:jpg|jpeg|png|webp))"',
            html, re.IGNORECASE
        )
        for img in images:
            if 'logo' not in img.lower() and 'icon' not in img.lower():
                meta.cover_url = img.strip()
                meta.poster_url = meta.cover_url
                break

    # Return None if no data was actually scraped
    if not meta.title_jp and not meta.cover_url:
        return None
    return meta

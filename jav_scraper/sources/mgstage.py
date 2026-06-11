"""MGStage scraper (mgstage.com)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://www.mgstage.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from MGStage."""
    num = number.upper()

    # Try various URL patterns
    urls = [
        f"{BASE_URL}/product/product_detail/{num}/",
        f"{BASE_URL}/product/product_detail/{num.replace('-', '')}/",
    ]
    # If number has no hyphen, try inserting one after prefix digits
    if '-' not in num:
        m = re.match(r'^(\d+)([A-Z].*)$', num)
        if m:
            alt = f"{m.group(1)}{m.group(2)}"
            urls.append(f"{BASE_URL}/product/product_detail/{alt}/")

    html = ""
    for url in urls:
        # Cookie adc=1 is needed; pass via headers
        html = fetch_text(url, headers={"Cookie": "adc=1"})
        if html and "product_detail" in html:
            break
        html = ""

    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="mgstage",
        image_cut="right",
    )

    # Title
    title_match = re.search(
        r'<h3[^>]*>\\s*([^<]+)\\s*</h3>', html, re.IGNORECASE
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    if not meta.title_jp:
        title_match = re.search(
            r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
        )
        if title_match:
            meta.title_jp = title_match.group(1).strip()
            meta.title_jp = re.sub(
                r'\\s*[-–|]\\s*MGStage.*$', '', meta.title_jp, flags=re.IGNORECASE
            ).strip()

    # Number
    id_match = re.search(
        r'商品番号[：:]\\s*</td>\\s*<td[^>]*>\\s*([^<\\s]+)',
        html, re.IGNORECASE
    )
    if id_match:
        meta.number = id_match.group(1).strip().upper()

    # Actress
    actress_match = re.search(
        r'出演者[：:]\\s*</td>\\s*<td[^>]*>\\s*([^<]+)',
        html, re.IGNORECASE
    )
    if actress_match:
        names = re.split(r'[、,，]', actress_match.group(1).strip())
        for name in names:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    if not meta.actors:
        actor_links = re.findall(
            r'<a[^>]*href="/[^"]*actress[^"]*"[^>]*>([^<]+)</a>',
            html, re.IGNORECASE
        )
        for name in actor_links:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # Cover
    cover_match = re.search(
        r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*picture_left[^"]*"',
        html, re.IGNORECASE
    )
    if not cover_match:
        cover_match = re.search(
            r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Release date
    date_match = re.search(
        r'発売日[：:]\\s*</td>\\s*<td[^>]*>\\s*([^<\\s]+)',
        html, re.IGNORECASE
    )
    if date_match:
        meta.release = date_match.group(1).strip()

    # Runtime
    runtime_match = re.search(
        r'収録時間[：:]\\s*</td>\\s*<td[^>]*>\\s*(\\d+)',
        html, re.IGNORECASE
    )
    if runtime_match:
        meta.runtime = runtime_match.group(1).strip()

    # Studio / Maker
    studio_match = re.search(
        r'メーカー[：:]\\s*</td>\\s*<td[^>]*>\\s*([^<]+)',
        html, re.IGNORECASE
    )
    if studio_match:
        meta.studio = studio_match.group(1).strip()
        meta.maker = meta.studio

    # Director
    dir_match = re.search(
        r'監督[：:]\\s*</td>\\s*<td[^>]*>\\s*([^<]+)',
        html, re.IGNORECASE
    )
    if dir_match:
        meta.director = dir_match.group(1).strip()

    # Series
    series_match = re.search(
        r'シリーズ[：:]\\s*</td>\\s*<td[^>]*>\\s*([^<]+)',
        html, re.IGNORECASE
    )
    if series_match:
        meta.series = series_match.group(1).strip()

    # Tags
    tags = re.findall(
        r'<a[^>]*href="/product/list/\\?keyword=[^"]*"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    # Description
    desc_match = re.search(
        r'<div[^>]*class="[^"]*introduction[^"]*"[^>]*>\\s*(.*?)</div>',
        html, re.IGNORECASE | re.DOTALL
    )
    if desc_match:
        desc = desc_match.group(1).strip()
        desc = re.sub(r'<[^>]+>', '', desc)
        meta.plot = desc.strip()

    return meta

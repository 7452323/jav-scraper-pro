"""7mmtv.sx scraper — JAV metadata source accessible globally."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text, get_session

BASE_URL = "https://7mmtv.sx"


def _search(number: str) -> str | None:
    """Search for a JAV number on 7mmtv using POST search."""
    num = number.upper().strip()

    try:
        session = get_session()
        resp = session.post(
            f"{BASE_URL}/en/searchform_search/all/index.html",
            data={"search_keyword": num, "op": "search"},
            headers={
                "Referer": f"{BASE_URL}/en/",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=30,
        )
        resp.raise_for_status()
        html = resp.text
    except Exception:
        return None

    # Look for product grid items in search results
    # Format: <a href='/en/censored_content/{id}/{number}.html'>
    # Sometimes results are in a JSON-LD script
    links = re.findall(
        rf'href="(/en/censored_content/\d+/{re.escape(num)}\.html)"',
        html, re.IGNORECASE
    )
    if links:
        return links[0]

    # Fallback: try the JA version
    try:
        resp = session.post(
            f"{BASE_URL}/ja/searchform_search/all/index.html",
            data={"search_keyword": num, "op": "search"},
            headers={
                "Referer": f"{BASE_URL}/ja/",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=30,
        )
        resp.raise_for_status()
        html = resp.text
    except Exception:
        return None

    links = re.findall(
        rf'href="(/ja/censored_content/\d+/{re.escape(num)}\.html)"',
        html, re.IGNORECASE
    )
    if links:
        return links[0]

    return None


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from 7mmtv.sx."""
    num = number.upper().strip()

    # Try search
    path = _search(num)
    if not path:
        return None

    # Fetch detail page
    url = BASE_URL + path
    html = fetch_text(url)
    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="7mmtv",
        mosaic="Censored",
    )

    # Title
    title_match = re.search(
        r'<h\d[^>]*class="[^"]*video[^"]*title[^"]*"[^>]*>\s*([^<]+)',
        html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    # Fallback: og:title
    if not meta.title_jp:
        og_match = re.search(
            r'<meta\s+property="og:title"[^>]*content="([^"]+)"',
            html, re.IGNORECASE
        )
        if og_match:
            meta.title_jp = og_match.group(1).strip()

    # Actors
    actor_names = re.findall(
        r'censored_avperformer/\d+/([^/]+)/1\.html',
        html, re.IGNORECASE
    )
    for name in set(actor_names):
        name_clean = name.strip()
        if name_clean:
            meta.actors.append(Actor(name=name_clean, role="actor"))

    # Studio / Maker
    studio_match = re.search(
        r'メーカー[：:]\s*</strong></div>\s*<div[^>]*>\s*<a[^>]*>\s*([^<]+)\s*</a>',
        html, re.IGNORECASE
    )
    if studio_match:
        meta.studio = studio_match.group(1).strip()
        meta.maker = meta.studio

    # Label
    label_match = re.search(
        r'レーベル[：:]\s*</strong></div>\s*<div[^>]*>\s*<a[^>]*>\s*([^<]+)\s*</a>',
        html, re.IGNORECASE
    )
    if label_match:
        meta.label = label_match.group(1).strip()

    # Director
    director_match = re.search(
        r'監督[：:]\s*</strong></div>\s*<div[^>]*>\s*<a[^>]*>\s*([^<]+)\s*</a>',
        html, re.IGNORECASE
    )
    if director_match:
        meta.director = director_match.group(1).strip()

    # Release date
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', html)
    if date_match:
        date_str = date_match.group(1)
        year = int(date_str[:4])
        if 2010 <= year <= 2030:
            meta.release = date_str
            meta.year = date_str[:4]

    # Runtime
    runtime_match = re.search(r'(\d+)\s*分<', html)
    if runtime_match:
        meta.runtime = runtime_match.group(1)

    # Tags / Genres
    tags = re.findall(
        r"class='btn btn-sm mb-1 me-1'[^>]*>\s*([^<]+)\s*</a>",
        html
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    # Cover image
    cover_match = re.search(
        r'src="(https://n1\.1026cdn\.sx[^"]+\.(?:jpg|jpeg|png))"',
        html, re.IGNORECASE
    )
    if not cover_match:
        # Fallback: DMM cover
        cover_match = re.search(
            r'src="(https://pics\.dmm\.co\.jp[^"]+jp-1\.jpg)"',
            html, re.IGNORECASE
        )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Return None if no real data
    if not meta.title_jp and not meta.cover_url:
        return None

    return meta

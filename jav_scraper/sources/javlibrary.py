"""JavLibrary scraper (javlibrary.com)."""

import re
import urllib.parse

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://www.javlibrary.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from JavLibrary."""
    num = number.upper()

    # JavLibrary uses a search-based approach
    search_url = (
        f"{BASE_URL}/en/?v=montlim&search={urllib.parse.quote(num)}"
    )
    html = fetch_text(search_url)
    if not html:
        return None

    # Find the first matching video link
    match = re.search(
        r'<a\s+href="([^"]*\/\?v\=[^"]+)"[^>]*>\s*<span[^>]*class="[^"]*title[^"]*"[^>]*>' +
        re.escape(num),
        html,
        re.IGNORECASE,
    )
    if not match:
        # Broader search
        match = re.search(
            r'<a\s+href="(/\?v=[a-z0-9]+)"[^>]*>',
            html,
            re.IGNORECASE,
        )
    if not match:
        # JavLibrary sometimes uses direct links
        match = re.search(
            r'<div[^>]*class="[^"]*video[^"]*"[^>]*>.*?<a\s+href="(/\?v=[^"]+)"',
            html,
            re.IGNORECASE | re.DOTALL,
        )
    if not match:
        return None

    href = match.group(1)
    if not href.startswith("http"):
        href = BASE_URL + href

    html = fetch_text(href)
    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="javlibrary",
    )

    # Title
    title_match = re.search(
        r'<title>\s*(.*?)\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        meta.title_jp = re.sub(
            r'\s*[-–|]\s*JAVLibrary.*$',
            '',
            meta.title_jp,
            flags=re.IGNORECASE,
        ).strip()

    # Also check for the main video title
    video_title_match = re.search(
        r'<div[^>]*id="video_title"[^>]*>.*?<h3[^>]*>\s*<a[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if video_title_match:
        meta.title_jp = video_title_match.group(1).strip()

    # Actors - JavLibrary uses star links
    star_links = re.findall(
        r'<span\s+class="[^"]*star[^"]*"[^>]*>\s*<a\s+href="[^"]*star[^"]*"[^>]*>\s*([^<\n]+)\s*</a>',
        html,
        re.IGNORECASE,
    )
    for name in star_links:
        name = name.strip()
        if name:
            meta.actors.append(Actor(name=name, role="actor"))

    # Director
    dir_match = re.search(
        r'<span\s+class="[^"]*director[^"]*"[^>]*>\s*<a\s+href="[^"]*director[^"]*"[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    if dir_match:
        meta.director = dir_match.group(1).strip()

    # Release date
    date_match = re.search(
        r'<span\s+class="[^"]*date[^"]*"[^>]*>\s*(\d{4}[-/]\d{2}[-/]\d{2})',
        html,
        re.IGNORECASE,
    )
    if date_match:
        meta.release = date_match.group(1).strip().replace("/", "-")

    # Runtime
    runtime_match = re.search(
        r'<span\s+class="[^"]*runtime[^"]*"[^>]*>\s*(\d+)',
        html,
        re.IGNORECASE,
    )
    if runtime_match:
        meta.runtime = runtime_match.group(1).strip()

    # Studio / Maker
    studio_match = re.search(
        r'<span\s+class="[^"]*studio[^"]*"[^>]*>\s*<a\s+href="[^"]*studio[^"]*"[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    if studio_match:
        meta.studio = studio_match.group(1).strip()
        meta.maker = meta.studio

    # Label
    label_match = re.search(
        r'<span\s+class="[^"]*label[^"]*"[^>]*>\s*<a\s+href="[^"]*label[^"]*"[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    if label_match:
        meta.publisher = label_match.group(1).strip()
        meta.label = meta.publisher

    # Genre / Tags
    genre_links = re.findall(
        r'<span\s+class="[^"]*genre[^"]*"[^>]*>\s*<a\s+href="[^"]*genre[^"]*"[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    meta.tags = [g.strip() for g in genre_links if g.strip()]

    # Score
    score_match = re.search(
        r'<span\s+class="[^"]*score[^"]*"[^>]*>\s*([\d.]+)',
        html,
        re.IGNORECASE,
    )
    if score_match:
        meta.score = score_match.group(1).strip()

    # Cover image
    cover_match = re.search(
        r'<img\s+[^>]*id="video_cover"[^>]*src="([^"]+)"',
        html,
        re.IGNORECASE,
    )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        # Ensure absolute URL
        if meta.cover_url.startswith("//"):
            meta.cover_url = "https:" + meta.cover_url
        elif meta.cover_url.startswith("/"):
            meta.cover_url = BASE_URL + meta.cover_url
        meta.poster_url = meta.cover_url

    # Also check for the big cover image
    if not meta.cover_url:
        cover_match = re.search(
            r'<a\s+href="([^"]+)"[^>]*>\s*<img[^>]*id="video_cover"',
            html,
            re.IGNORECASE,
        )
        if cover_match:
            meta.cover_url = cover_match.group(1).strip()
            if meta.cover_url.startswith("//"):
                meta.cover_url = "https:" + meta.cover_url
            meta.poster_url = meta.cover_url

    # Description / Plot
    desc_match = re.search(
        r'<div[^>]*id="video_description"[^>]*>\s*(.*?)</div>',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if desc_match:
        meta.plot = desc_match.group(1).strip()
        meta.plot = re.sub(r'<[^>]+>', '', meta.plot)
        meta.plot = re.sub(r'\s+', ' ', meta.plot).strip()

    return meta

"""AI-Rav scraper (airav.wiki)."""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://cn.airav.wiki"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from AI-Rav Wiki."""
    num = number.upper()

    # Try direct video page
    url = f"{BASE_URL}/video/{num}"
    html = fetch_text(url)
    if not html:
        url = f"{BASE_URL}/video/{num.lower()}"
        html = fetch_text(url)
    if not html:
        # Try search
        search_url = f"{BASE_URL}/search?q={num}"
        html = fetch_text(search_url)
        if not html:
            return None

        # Try to find a result link
        match = re.search(
            r'<a\\s+href="([^"]+)"[^>]*class="[^"]*video-title[^"]*"',
            html, re.IGNORECASE
        )
        if not match:
            match = re.search(
                r'<a\\s+href="/video/([^"]+)"',
                html, re.IGNORECASE
            )
        if not match:
            return None

        href = match.group(1)
        if href.startswith("/"):
            href = BASE_URL + href
        html = fetch_text(href)
        if not html:
            return None

    meta = JavMetadata(
        number=num,
        source="airav",
        image_cut="right",
    )

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
        meta.title_jp = re.sub(
            r'\\s*[-–|]\\s*AI-Rav.*$', '', meta.title_jp, flags=re.IGNORECASE
        ).strip()

    # Try to get CN title
    cn_match = re.search(
        r'<h1[^>]*>\\s*([^<]+)\\s*</h1>', html, re.IGNORECASE
    )
    if cn_match:
        t = cn_match.group(1).strip()
        if t and len(t) > 3:
            meta.title_cn = t

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

    # Actors
    actor_links = re.findall(
        r'<a[^>]*href="/actor/[^"]+"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    for name in actor_links:
        name = name.strip()
        if name:
            meta.actors.append(Actor(name=name, role="actor"))

    if not meta.actors:
        actor_text = re.search(
            r'出演[：:]\\s*([^<]+)', html, re.IGNORECASE
        )
        if actor_text:
            names = re.split(r'[、,，/]', actor_text.group(1).strip())
            for name in names:
                name = name.strip()
                if name:
                    meta.actors.append(Actor(name=name, role="actor"))

    # Tags
    tags = re.findall(
        r'<a[^>]*href="/tag/[^"]+"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    meta.tags = [t.strip() for t in tags if t.strip()]

    return meta

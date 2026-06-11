"""JAVCL scraper (javcl.com) — WordPress-based JAV streaming site."""
import re
import urllib.parse

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://javcl.com"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from javcl.com."""
    num = number.upper().strip()

    # Try direct URL first: /movie/{number} redirects to /{number}-slug/
    direct_url = f"{BASE_URL}/movie/{num.lower()}"
    html = fetch_text(direct_url)
    if not html:
        return None

    # Check if redirected (the actual post URL)
    # Find canonical URL
    canon_match = re.search(
        r'<link[^>]*rel=canonical[^>]*href="([^"]+)"',
        html, re.IGNORECASE
    )
    if canon_match and canon_match.group(1) != direct_url:
        post_url = canon_match.group(1)
        html2 = fetch_text(post_url)
        if html2:
            html = html2

    meta = JavMetadata(
        number=num,
        source="javcl",
        studio="FALENO",
        maker="FALENO",
        mosaic="Censored",
    )

    # Title from <title>
    title_match = re.search(
        r'<title>([^<]+)</title>', html, re.IGNORECASE
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    # Fallback: og:title
    if not meta.title_jp:
        og_match = re.search(
            r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"',
            html, re.IGNORECASE
        )
        if og_match:
            meta.title_jp = og_match.group(1).strip()

    # Cover from og:image
    cover_match = re.search(
        r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Actors — look for model links (href may be quoted or unquoted)
    actor_links = re.findall(
        r'<a[^>]*href=[\"\']?https://javcl\.com/model/[^\"\'>\s]+[\"\']?[^>]*>([^<]+)',
        html, re.IGNORECASE
    )
    for name in actor_links:
        name = name.strip().rstrip(',').strip()
        if name and name not in ("admin", "admin2", "MODEL"):
            meta.actors.append(Actor(name=name, role="actor"))

    # Studio/maker from article content if present
    studio_match = re.search(
        r'product by\s+([^,.<]+)', html, re.IGNORECASE
    )
    if studio_match:
        meta.studio = studio_match.group(1).strip()
        meta.maker = meta.studio

    # Keywords / Tags from JSON-LD
    kw_match = re.search(
        r'"keywords":\s*\[([^\]]+)\]', html, re.IGNORECASE
    )
    if kw_match:
        kw_text = kw_match.group(1)
        tags = re.findall(r'"([^"]+)"', kw_text)
        meta.tags = [t.strip() for t in tags if t.strip()]

    if not meta.tags:
        # Try articleSection
        sec_match = re.search(
            r'"articleSection":\s*\[([^\]]+)\]', html, re.IGNORECASE
        )
        if sec_match:
            sec_text = sec_match.group(1)
            tags = re.findall(r'"([^"]+)"', sec_text)
            meta.tags = [t.strip() for t in tags if t.strip()]

    # Date from JSON-LD
    date_match = re.search(
        r'"datePublished":\s*"([^"]+)"', html, re.IGNORECASE
    )
    if date_match:
        date_str = date_match.group(1)[:10]  # YYYY-MM-DD
        meta.release = date_str
        meta.year = date_str[:4]

    # Description
    desc_match = re.search(
        r'<meta[^>]*name="description"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if desc_match:
        meta.plot = desc_match.group(1).strip()

    if not meta.title_jp and not meta.cover_url:
        return None

    return meta

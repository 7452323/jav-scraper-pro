"""DMM/FANZA scraper (dmm.co.jp) — the largest JAV retailer.

Uses DMM's public product pages. Falls back to search if direct CID lookup fails.
Note: DMM may block non-Japanese IPs; gracefully returns None if blocked.
"""

import re
import logging

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

logger = logging.getLogger(__name__)

# DMM domains to try (some may redirect)
DOMAINS = [
    "https://www.dmm.co.jp",
    "https://www.dmm.com",
    "https://dmm.co.jp",
]


def _to_cid(number: str) -> str:
    """Convert JAV number to DMM CID format.

    FNS-215  -> fns00215
    MIDV-001 -> midv00001 (keep leading zeros)
    ABW-123  -> abw00123
    FC2-1234567 -> fc21234567 (FC2 format: no padding)
    """
    num = number.upper().strip()
    m = re.match(r'^([A-Z]+)[-_]?(\d+)$', num)
    if m:
        prefix = m.group(1).lower()
        digits = m.group(2)
        # FC2: no zero-padding
        if prefix == "fc2":
            return f"{prefix}{digits}"
        # Standard: zero-pad to 5 digits
        return prefix + digits.zfill(5)
    return num.lower().replace("-", "").replace("_", "")


def _scrape_page(html: str) -> JavMetadata | None:
    """Parse metadata from a DMM product page HTML."""
    meta = JavMetadata(source="dmm", mosaic="Censored", image_cut="right")

    # --- Title ---
    title_match = re.search(
        r'<h1[^>]*id="title"[^>]*>(.*?)</h1>',
        html, re.IGNORECASE | re.DOTALL
    )
    if not title_match:
        # Fallback: common heading
        title_match = re.search(
            r'<h1[^>]*class="[^"]*productTitle[^"]*"[^>]*>(.*?)</h1>',
            html, re.IGNORECASE | re.DOTALL
        )
    if not title_match:
        # Fallback: any h1
        title_match = re.search(
            r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL
        )
    if title_match:
        meta.title_jp = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()

    # Fallback: og:title
    if not meta.title_jp:
        og_match = re.search(
            r'<meta\s+property="og:title"[^>]*content="([^"]+)"',
            html, re.IGNORECASE
        )
        if og_match:
            meta.title_jp = og_match.group(1).strip()
            # Strip site name suffix like " | FANZA"
            meta.title_jp = re.sub(r'\s*[|│].*$', '', meta.title_jp).strip()

    # --- Check if this is a valid product page ---
    # DMM returns service messages for retired products
    if meta.title_jp and re.search(
        r'サービス統合|サービス終了|お知らせ|404|Not Found',
        meta.title_jp, re.IGNORECASE
    ):
        return None

    # --- Cover image ---
    cover_match = re.search(
        r'<a\s+[^>]*name="packageImage"[^>]*href="([^"]+)"',
        html, re.IGNORECASE
    )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        # Make absolute if relative
        if meta.cover_url.startswith("//"):
            meta.cover_url = "https:" + meta.cover_url
        elif meta.cover_url.startswith("/"):
            meta.cover_url = "https://www.dmm.co.jp" + meta.cover_url
        meta.poster_url = meta.cover_url

    # Fallback: og:image
    if not meta.cover_url:
        og_match = re.search(
            r'<meta\s+property="og:image"[^>]*content="([^"]+)"',
            html, re.IGNORECASE
        )
        if og_match:
            meta.cover_url = og_match.group(1).strip()
            meta.poster_url = meta.cover_url

    # --- Table info (配信開始日, 収録時間, シリーズ, メーカー, 監督, etc.) ---
    # DMM puts info in a table with class or just plain text labels
    info_sections = [
        # Pattern: label: value<br>
        r'>([^<]*発売日[^<]*)</td>\s*<td[^>]*>([^<]+)',
        r'>([^<]*収録時間[^<]*)</td>\s*<td[^>]*>([^<]+)',
        r'>([^<]*メーカー[^<]*)</td>\s*<td[^>]*>([^<]+)',
        r'>([^<]*シリーズ[^<]*)</td>\s*<td[^>]*>([^<]+)',
        r'>([^<]*監督[^<]*)</td>\s*<td[^>]*>([^<]+)',
        r'>([^<]*ジャンル[^<]*)</td>\s*<td[^>]*>([^<]+)',
    ]

    for pattern in info_sections:
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            label = m.group(1).strip()
            value = m.group(2).strip()
            value = re.sub(r'<[^>]+>', '', value).strip()

            if '発売日' in label or '配信開始日' in label:
                # Format: 2024/01/01 -> 2024-01-01
                date_clean = value.replace('/', '-')
                meta.release = date_clean
                if len(date_clean) >= 4:
                    meta.year = date_clean[:4]
            elif '収録時間' in label:
                m_runtime = re.search(r'(\d+)', value)
                if m_runtime:
                    meta.runtime = m_runtime.group(1)
            elif 'メーカー' in label:
                meta.studio = value
                meta.maker = value
            elif 'シリーズ' in label:
                meta.series = value
            elif '監督' in label:
                meta.director = value
            elif 'ジャンル' in label or 'ジャンル' in label:
                # Tags: <a> links inside the cell
                tag_matches = re.findall(
                    r'<a[^>]*>([^<]+)</a>', value, re.IGNORECASE
                )
                meta.tags = [t.strip() for t in tag_matches if t.strip()]

    # --- Tags from genre links ---
    if not meta.tags:
        tag_matches = re.findall(
            r'<a\s+href="[^"]*/digital/videoa/-/list/=/article=genre/'
            r'[^"]*"[^>]*>\s*([^<]+)\s*</a>',
            html, re.IGNORECASE
        )
        meta.tags = [t.strip() for t in tag_matches if t.strip()]

    # --- Actors ---
    # DMM: actress links
    actor_matches = re.findall(
        r'<a\s+href="[^"]*/digital/videoa/-/list/=/article=actress/'
        r'[^"]*"[^>]*>\s*([^<]+)\s*</a>',
        html, re.IGNORECASE
    )
    for name in actor_matches:
        name = name.strip()
        if name:
            meta.actors.append(Actor(name=name, role="actor"))

    # Also try simpler patterns
    if not meta.actors:
        actor_matches = re.findall(
            r'<span[^>]*class="[^"]*actorName[^"]*"[^>]*>\s*([^<]+)\s*</span>',
            html, re.IGNORECASE
        )
        for name in actor_matches:
            name = name.strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # --- Description / Plot ---
    # DMM uses div with id="productDescription" or similar
    desc_match = re.search(
        r'<div[^>]*class="[^"]*productDescription[^"]*"[^>]*>'
        r'\s*(.*?)\s*</div>',
        html, re.IGNORECASE | re.DOTALL
    )
    if desc_match:
        meta.plot = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()
        # Clean up whitespace
        meta.plot = re.sub(r'\s+', ' ', meta.plot).strip()

    # --- Sample images ---
    sample_matches = re.findall(
        r'<a\s+href="([^"]+)"[^>]*class="[^"]*sampleBox[^"]*"',
        html, re.IGNORECASE
    )
    meta.extrafanart = [s.strip() for s in sample_matches if s.strip()]

    # --- Score (if available on DMM) ---
    score_match = re.search(
        r'<span[^>]*class="[^"]*rating[^"]*"[^>]*>\s*([\d.]+)',
        html, re.IGNORECASE
    )
    if score_match:
        meta.score = score_match.group(1).strip()

    # --- Check if we got at least a title ---
    if not meta.title_jp:
        logger.debug("DMM: No title found")
        return None

    return meta


def _try_search(number: str) -> JavMetadata | None:
    """Search DMM for the number and follow the first result."""
    for domain in DOMAINS:
        search_url = f"{domain}/search/=/searchstr={number}/"
        html = fetch_text(search_url)
        if not html:
            continue

        # Find the first product link
        # DMM search results link to detail pages
        link_match = re.search(
            r'<a\s+href="(/digital/videoa/[^"]+/detail[^"]*)"[^>]*>'
            r'\s*<img[^>]*src="[^"]*[Pp]ackage[^"]*"',
            html, re.IGNORECASE | re.DOTALL
        )
        if not link_match:
            link_match = re.search(
                r'<a\s+href="(/digital/videoa/[^"]+)"[^>]*>'
                r'\s*<img[^>]*alt="[^"]*' + re.escape(number) + r'[^"]*"',
                html, re.IGNORECASE | re.DOTALL
            )
        if not link_match:
            continue

        product_path = link_match.group(1)
        if not product_path.startswith("http"):
            product_url = domain + product_path
        else:
            product_url = product_path

        product_html = fetch_text(product_url)
        if product_html:
            meta = _scrape_page(product_html)
            if meta:
                return meta

    return None


def _try_direct(number: str) -> JavMetadata | None:
    """Try direct CID lookup on DMM."""
    cid = _to_cid(number)
    paths = [
        f"/digital/videoa/-/detail/=/cid={cid}/",
        f"/digital/videoa/-/detail/=/cid={number.lower().replace('-', '')}/",
        f"/digital/videoa/-/detail/=/cid={number.lower()}/",
    ]

    for domain in DOMAINS:
        for path in paths:
            url = domain + path
            html = fetch_text(url)
            if html:
                meta = _scrape_page(html)
                if meta:
                    return meta
    return None


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from DMM/FANZA.

    Tries direct CID lookup first, then falls back to search.
    """
    num = number.upper().strip()

    # Try direct CID lookup
    meta = _try_direct(num)
    if meta:
        meta.number = num
        return meta

    # Fall back to search
    meta = _try_search(num)
    if meta:
        meta.number = num
        return meta

    return None

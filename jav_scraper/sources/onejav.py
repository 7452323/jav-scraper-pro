"""OneJAV scraper (onejav.com) — JAV torrent site with Japanese metadata."""
import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

BASE_URL = "https://onejav.com"


def _find_torrent_page(number: str, html: str) -> str | None:
    """Find the torrent page link from search results."""
    num_lower = number.lower().replace("-", "")
    all_links = re.findall(
        r'<a\s+href="(/(?:torrent)/[^"]+)"[^>]*>\s*([^<]+)',
        html,
        re.IGNORECASE,
    )
    for link_href, link_text in all_links:
        link_clean = link_text.strip().lower().replace("-", "")
        if link_clean == num_lower:
            return link_href
    # fallback: any link containing the number
    for link_href, link_text in all_links:
        if num_lower in link_href.lower():
            return link_href
    return None


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from OneJAV."""
    num = number.upper().strip()
    num_lower = number.lower()

    # Try direct torrent page first (onejav URLs use no hyphen, e.g. snos141)
    html = fetch_text(f"{BASE_URL}/torrent/{num_lower.replace('-', '')}")
    if not html or "torrent" not in html.lower():
        # Fallback: search
        html = fetch_text(f"{BASE_URL}/search/{num_lower.replace('-', '')}/")
        if not html:
            return None
        link = _find_torrent_page(num, html)
        if not link:
            return None
        html = fetch_text(BASE_URL + link)
        if not html:
            return None

    meta = JavMetadata(
        number=num,
        source="onejav",
        mosaic="Censored",
    )

    # --- Japanese title ---
    # 1. Try <p class="level has-text-grey-dark"> (the main Japanese title display)
    title_match = re.search(
        r'<p\s+class="level\s+has-text-grey-dark">\s*([^<]+)\s*</p>',
        html, re.IGNORECASE
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()
    else:
        # 2. Try meta description (contains Japanese title)
        desc_match = re.search(
            r'<meta\s+name="description"[^>]*content="[^"]*-\s*([^"]+?)\s*,\s*Actress:',
            html, re.IGNORECASE
        )
        if desc_match:
            meta.title_jp = desc_match.group(1).strip()
        else:
            # 3. Try OG description
            og_desc = re.search(
                r'<meta\s+property="og:description"[^>]*content="[^"]*-\s*([^"]+?)\s*,\s*Actress:',
                html, re.IGNORECASE
            )
            if og_desc:
                meta.title_jp = og_desc.group(1).strip()
            else:
                # 4. Fallback: <title> tag
                title_tag = re.search(
                    r'<title>\s*(.*?)\s*</title>', html, re.IGNORECASE | re.DOTALL
                )
                if title_tag:
                    meta.title_jp = title_tag.group(1).strip()
                    meta.title_jp = re.sub(
                        r'\s*[-–|]\s*OneJAV\..*$', '', meta.title_jp, flags=re.IGNORECASE
                    ).strip()

    # --- Actors ---
    # OneJAV uses /actress/ links (not /actor/)
    actor_matches = re.findall(
        r'<a\s+class="panel-block"[^>]*href="/actress/[^"]+"[^>]*>([^<]+)</a>',
        html, re.IGNORECASE
    )
    for name in actor_matches:
        meta.actors.append(Actor(name=name.strip(), role="actor"))

    # --- Date ---
    # OneJAV breadcrumb: <li><a href="/2026/01/08">Jan. 8, 2026</a></li>
    date_match = re.search(
        r'href="/(\d{4})/(\d{2})/(\d{2})">',
        html, re.IGNORECASE
    )
    if date_match:
        meta.release = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        meta.year = date_match.group(1)

    # --- Cover image + studio ---
    cover_match = re.search(
        r'<meta\s+property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url
        # Extract studio from image URL: /images/prestige/abf/ → Prestige
        studio_match = re.search(r'/images/([^/]+)/', meta.cover_url, re.IGNORECASE)
        if studio_match:
            meta.studio = studio_match.group(1).strip().capitalize()
            meta.maker = meta.studio
            meta.label = meta.studio
    else:
        img_match = re.search(
            r'<img[^>]*class="image"[^>]*src="([^"]+)"',
            html, re.IGNORECASE
        )
        if img_match:
            meta.cover_url = img_match.group(1).strip()
            meta.poster_url = meta.cover_url

    # Check if we got real data
    if not meta.title_jp and not meta.cover_url:
        return None

    return meta

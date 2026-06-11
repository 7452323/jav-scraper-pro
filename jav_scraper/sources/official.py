"""Official site generic scraper.

Attempts known site patterns based on number prefix to fetch metadata.
"""

import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

# Known prefix-to-site mappings
PREFIX_MAP = {
    "ABW": "https://www.prestige-av.com",
    "ABP": "https://www.prestige-av.com",
    "ABS": "https://www.prestige-av.com",
    "AB": "https://www.prestige-av.com",
    "BGN": "https://www.prestige-av.com",
    "BGS": "https://www.prestige-av.com",
    "BJK": "https://www.prestige-av.com",
    "BKD": "https://www.prestige-av.com",
    "BMS": "https://www.prestige-av.com",
    "BND": "https://www.prestige-av.com",
    "BOK": "https://www.prestige-av.com",
    "BUR": "https://www.prestige-av.com",
    "BWD": "https://www.prestige-av.com",
    "CES": "https://www.prestige-av.com",
    "CHB": "https://www.prestige-av.com",
    "DANDY": "https://www.dandy-movie.com",
    "DBN": "https://www.prestige-av.com",
    "DDT": "https://www.prestige-av.com",
    "DIANA": "https://www.prestige-av.com",
    "DIC": "https://www.prestige-av.com",
    "DJN": "https://www.prestige-av.com",
    "DJO": "https://www.prestige-av.com",
    "DOK": "https://www.prestige-av.com",
    "EBOD": "https://www.ebod.tv",
    "FALENO": "https://faleno.com",
    "FSDSS": "https://faleno.com",
    "FCDSS": "https://faleno.com",
    "GVH": "https://gv-h.com",
    "HMN": "https://faleno.com",
    "IPZ": "https://www.ideapocket.com",
    "IPX": "https://www.ideapocket.com",
    "IPTD": "https://www.ideapocket.com",
    "JUFE": "https://www.ideapocket.com",
    "JUL": "https://www.madonna-av.com",
    "JVN": "https://www.prestige-av.com",
    "KAWD": "https://www.kawaiikawaii.jp",
    "KIS": "https://www.prestige-av.com",
    "KPN": "https://www.prestige-av.com",
    "LULU": "https://www.prestige-av.com",
    "MADV": "https://www.madonna-av.com",
    "MCB": "https://www.prestige-av.com",
    "MDTM": "https://www.prestige-av.com",
    "MGT": "https://www.prestige-av.com",
    "MIAE": "https://www.prestige-av.com",
    "MIUM": "https://www.mgstage.com",
    "MKS": "https://www.prestige-av.com",
    "MMK": "https://www.prestige-av.com",
    "MOP": "https://www.prestige-av.com",
    "MS": "https://www.moodyz.com",
    "MT": "https://www.prestige-av.com",
    "MVSD": "https://www.moodyz.com",
    "NACR": "https://www.prestige-av.com",
    "NADE": "https://www.prestige-av.com",
    "NIMA": "https://www.prestige-av.com",
    "NKK": "https://www.prestige-av.com",
    "NKR": "https://www.prestige-av.com",
    "NTR": "https://www.prestige-av.com",
    "OBA": "https://www.prestige-av.com",
    "OKS": "https://www.prestige-av.com",
    "PBD": "https://www.prestige-av.com",
    "PBL": "https://www.prestige-av.com",
    "PPPD": "https://www.oppai-av.com",
    "PRED": "https://www.prestige-av.com",
    "RMS": "https://www.prestige-av.com",
    "SAME": "https://www.prestige-av.com",
    "SGS": "https://www.prestige-av.com",
    "SHIC": "https://www.prestige-av.com",
    "SIVR": "https://www.prestige-av.com",
    "SKY": "https://www.prestige-av.com",
    "SMA": "https://www.prestige-av.com",
    "SOE": "https://www.s1s1s1.com",
    "SRS": "https://www.prestige-av.com",
    "SS": "https://www.prestige-av.com",
    "STARS": "https://www.prestige-av.com",
    "STCV": "https://www.prestige-av.com",
    "STTL": "https://www.prestige-av.com",
    "SUG": "https://www.prestige-av.com",
    "SUKE": "https://www.prestige-av.com",
    "SVV": "https://www.prestige-av.com",
    "T-": "https://www.prestige-av.com",
    "TAGP": "https://www.prestige-av.com",
    "TAM": "https://www.prestige-av.com",
    "TEP": "https://www.prestige-av.com",
    "TRP": "https://www.prestige-av.com",
    "UCH": "https://www.prestige-av.com",
    "VENU": "https://www.prestige-av.com",
    "VSP": "https://www.prestige-av.com",
    "WAN": "https://www.prestige-av.com",
    "WSS": "https://www.prestige-av.com",
    "X ART": "https://www.xart.xxx",
    "XVSR": "https://www.max-a.co.jp",
    "ZEX": "https://www.prestige-av.com",
}


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from official site based on number prefix."""
    num = number.upper().strip()

    # Extract prefix
    prefix = ""
    m = re.match(r'^([A-Z]+[-_]?)', num)
    if m:
        prefix = m.group(1).rstrip("-").rstrip("_")

    # Look up site
    site_url = None
    if prefix in PREFIX_MAP:
        site_url = PREFIX_MAP[prefix]

    if not site_url:
        return None

    # Try common URL patterns
    url_patterns = [
        f"{site_url}/products/{num.lower()}/",
        f"{site_url}/product/{num.lower()}/",
        f"{site_url}/works/{num.lower()}/",
        f"{site_url}/detail/{num.lower()}/",
        f"{site_url}/movies/{num.lower()}",
        f"{site_url}/product/{num}/",
    ]

    html = ""
    for url in url_patterns:
        html = fetch_text(url)
        if html:
            break

    if not html:
        return None

    meta = JavMetadata(
        number=num,
        source="official",
        image_cut="right",
    )

    # Title
    title_match = re.search(
        r'<title>\\s*(.*?)\\s*</title>', html, re.IGNORECASE | re.DOTALL
    )
    if title_match:
        meta.title_jp = title_match.group(1).strip()

    h1_match = re.search(
        r'<h1[^>]*>\\s*([^<]+)\\s*</h1>', html, re.IGNORECASE
    )
    if h1_match:
        t = h1_match.group(1).strip()
        if t and len(t) > 3:
            meta.title_jp = t

    # Cover
    cover_match = re.search(
        r'<meta\\s+property="og:image"[^>]*content="([^"]+)"',
        html, re.IGNORECASE
    )
    if cover_match:
        meta.cover_url = cover_match.group(1).strip()
        meta.poster_url = meta.cover_url

    # Set studio based on prefix
    if site_url:
        domain = re.sub(r'https?://(www\\.)?', '', site_url)
        meta.studio = domain.split(".")[0].upper() if domain else ""
        meta.maker = meta.studio

    return meta

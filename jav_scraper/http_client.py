"""HTTP client with retry, session management, and proxy support."""

import os

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})

# Proxy support: respect HTTPS_PROXY / HTTP_PROXY env vars
_proxy_url = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or ""
if _proxy_url:
    _session.proxies.update({"https": _proxy_url, "http": _proxy_url})
    import logging
    logging.getLogger(__name__).info("Using proxy: %s", _proxy_url)


def get_session() -> requests.Session:
    return _session


def fetch(url: str, headers: dict | None = None, timeout: int = 30) -> requests.Response | None:
    """Fetch a URL with error handling."""
    try:
        h = {"User-Agent": USER_AGENT}
        if headers:
            h.update(headers)
        resp = _session.get(url, headers=h, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception:
        return None


def fetch_text(url: str, headers: dict | None = None, timeout: int = 30) -> str:
    """Fetch a URL and return text content."""
    r = fetch(url, headers, timeout)
    return r.text if r else ""


def fetch_bytes(url: str, headers: dict | None = None, timeout: int = 30) -> bytes | None:
    """Fetch a URL and return raw bytes."""
    r = fetch(url, headers, timeout)
    return r.content if r else None

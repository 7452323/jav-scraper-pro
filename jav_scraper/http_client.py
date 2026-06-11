"""HTTP client with retry and session management."""

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


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

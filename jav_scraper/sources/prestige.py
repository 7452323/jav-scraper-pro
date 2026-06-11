"""Prestige scraper (prestige-av.com)."""

import json
import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

SEARCH_URL = "https://www.prestige-av.com/api/search?searchText={number}"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from Prestige AV via JSON API."""
    num = number.upper()

    url = SEARCH_URL.format(number=num)
    resp_text = fetch_text(url, headers={"Accept": "application/json"})
    if not resp_text:
        return None

    try:
        data = json.loads(resp_text)
    except json.JSONDecodeError:
        return None

    # The response structure varies; try common patterns
    items = None
    if isinstance(data, dict):
        items = data.get("data") or data.get("results") or data.get("items")
    elif isinstance(data, list):
        items = data

    if not items:
        return None

    if isinstance(items, list) and len(items) > 0:
        item = items[0]
    elif isinstance(items, dict):
        item = items
    else:
        return None

    meta = JavMetadata(
        number=num,
        source="prestige",
        studio="Prestige",
        maker="Prestige",
        image_cut="right",
    )

    # Title
    title = item.get("title") or item.get("name") or ""
    if title:
        meta.title_jp = title.strip()

    # Number
    pid = item.get("id") or item.get("productId") or item.get("number") or ""
    if pid:
        meta.number = str(pid).upper()

    # Actors
    actors = item.get("actress") or item.get("actors") or item.get("actresses") or []
    if isinstance(actors, str):
        actors = [actors]
    for act in actors:
        if isinstance(act, dict):
            name = act.get("name") or ""
        else:
            name = str(act).strip()
        if name:
            meta.actors.append(Actor(name=name, role="actor"))

    # Cover
    cover = item.get("cover") or item.get("image") or item.get("coverUrl") or item.get("thumb") or ""
    if cover:
        meta.cover_url = cover.strip()
        meta.poster_url = meta.cover_url

    # Release date
    release = item.get("release") or item.get("date") or item.get("releaseDate") or ""
    if release:
        meta.release = release.strip()

    # Studio
    studio = item.get("studio") or item.get("maker") or ""
    if studio:
        if isinstance(studio, dict):
            studio = studio.get("name") or ""
        meta.studio = str(studio).strip() or meta.studio
        meta.maker = meta.studio

    return meta

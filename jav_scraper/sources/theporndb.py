"""ThePornDB scraper (api.theporndb.net)."""

import json
import re

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

API_URL = "https://api.theporndb.net/scenes?parse={number}"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from ThePornDB via JSON API."""
    num = number.upper()

    url = API_URL.format(number=num)
    resp_text = fetch_text(url, headers={"Accept": "application/json"})
    if not resp_text:
        return None

    try:
        data = json.loads(resp_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    # Extract first result
    scenes = None
    if "data" in data and isinstance(data["data"], list):
        scenes = data["data"]
    elif "scenes" in data and isinstance(data["scenes"], list):
        scenes = data["scenes"]

    if not scenes or len(scenes) == 0:
        return None

    item = scenes[0]

    meta = JavMetadata(
        number=num,
        source="theporndb",
        image_cut="left",
    )

    # Title
    title = item.get("title") or ""
    if title:
        meta.title_jp = title.strip()

    # Number / ID
    pid = item.get("id") or item.get("scene_id") or ""
    if pid:
        meta.number = str(pid).upper()

    # Actors
    performers = item.get("performers") or item.get("actors") or []
    for perf in performers:
        if isinstance(perf, dict):
            name = perf.get("name") or perf.get("stage_name") or ""
        else:
            name = str(perf).strip()
        if name:
            meta.actors.append(Actor(name=name.strip(), role="actor"))

    # Cover
    cover = item.get("background") or item.get("cover") or item.get("poster") or ""
    if cover:
        meta.cover_url = cover.strip()
        meta.poster_url = meta.cover_url

    # Tags
    tags_list = item.get("tags") or item.get("categories") or []
    for tag in tags_list:
        if isinstance(tag, dict):
            t = tag.get("name") or ""
        else:
            t = str(tag).strip()
        if t:
            meta.tags.append(t.strip())

    # Studio
    studio = item.get("studio") or item.get("site") or ""
    if isinstance(studio, dict):
        studio = studio.get("name") or ""
    if studio:
        meta.studio = str(studio).strip()
        meta.maker = meta.studio

    # Release date
    release = item.get("date") or item.get("release_date") or item.get("release") or ""
    if release:
        meta.release = str(release).strip()

    return meta

"""HDouban scraper (api.6dccbca.com)."""

import json
import re
import urllib.parse

from jav_scraper.metadata import Actor, JavMetadata
from jav_scraper.http_client import fetch_text

API_URL = "https://api.6dccbca.com/api/search?search={number}&ty=movie&page=1&pageSize=12"


def scrape(number: str) -> JavMetadata | None:
    """Scrape metadata from HDouban API."""
    num = number.upper()

    url = API_URL.format(number=urllib.parse.quote(num))
    resp_text = fetch_text(url, headers={"Accept": "application/json"})
    if not resp_text:
        return None

    try:
        data = json.loads(resp_text)
    except json.JSONDecodeError:
        return None

    meta = JavMetadata(
        number=num,
        source="hdouban",
        image_cut="right",
    )

    # Extract data from response
    results = None
    if isinstance(data, dict):
        results = data.get("data") or data.get("results") or data.get("list")
    elif isinstance(data, list):
        results = data

    if not results:
        return meta

    if isinstance(results, list) and len(results) > 0:
        item = results[0]
    elif isinstance(results, dict):
        item = results
    else:
        return meta

    # Title
    title = item.get("title") or item.get("name") or item.get("vod_title") or ""
    if title:
        meta.title_jp = title.strip()

    # CN title
    cn_title = item.get("vod_title_cn") or item.get("vod_title") or item.get("title_cn") or ""
    if cn_title:
        meta.title_cn = cn_title.strip()

    # Number / ID
    vid = item.get("vod_id") or item.get("id") or item.get("number") or ""
    if vid:
        meta.number = str(vid).upper()

    # Cover
    cover = item.get("vod_pic") or item.get("pic") or item.get("cover") or item.get("img") or ""
    if cover:
        if cover.startswith("/"):
            cover = "https:" + cover
        meta.cover_url = cover.strip()
        meta.poster_url = meta.cover_url

    # Actors
    actors_str = item.get("vod_actor") or item.get("actor") or item.get("actors") or ""
    if actors_str:
        if isinstance(actors_str, str):
            names = re.split(r'[、,，/\\s]+', actors_str)
        elif isinstance(actors_str, list):
            names = actors_str
        else:
            names = []
        for name in names:
            name = str(name).strip()
            if name:
                meta.actors.append(Actor(name=name, role="actor"))

    # Director
    director = item.get("vod_director") or item.get("director") or ""
    if director:
        if isinstance(director, str):
            meta.director = director.strip()
        elif isinstance(director, dict):
            meta.director = director.get("name") or ""

    # Release date
    release = item.get("vod_year") or item.get("year") or item.get("release") or item.get("vod_pubdate") or ""
    if release:
        meta.release = str(release).strip()

    # Tags
    tags_str = item.get("vod_class") or item.get("type_name") or item.get("tags") or ""
    if tags_str:
        if isinstance(tags_str, str):
            meta.tags = [t.strip() for t in re.split(r'[、,，/]', tags_str) if t.strip()]
        elif isinstance(tags_str, list):
            meta.tags = [str(t).strip() for t in tags_str if str(t).strip()]

    # Description
    desc = item.get("vod_content") or item.get("content") or item.get("description") or item.get("plot") or ""
    if desc:
        meta.plot = desc.strip()

    # Runtime
    runtime = item.get("vod_length") or item.get("length") or item.get("runtime") or ""
    if runtime:
        meta.runtime = str(runtime).strip()

    # Score
    score = item.get("vod_score") or item.get("score") or item.get("rating") or ""
    if score:
        meta.score = str(score).strip()

    return meta

"""NFO generator — Kodi/Emby/Jellyfin NFO builder."""

import logging
import os
import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from jav_scraper.metadata import JavMetadata

logger = logging.getLogger(__name__)


def _text_element(parent: Element, tag: str, text: str | None) -> None:
    """Add a text sub-element if text is non-empty."""
    if text:
        el = SubElement(parent, tag)
        el.text = text.strip()


def _genres_element(parent: Element, tags: list[str]) -> None:
    """Add genre elements from a list of tags."""
    for tag in tags:
        if tag:
            _text_element(parent, "genre", tag)


def _actors_element(parent: Element, meta: JavMetadata) -> None:
    """Add actor elements."""
    for actor in meta.actors:
        if actor.name:
            actor_el = SubElement(parent, "actor")
            _text_element(actor_el, "name", actor.name)
            _text_element(actor_el, "role", actor.role or "actor")
            _text_element(actor_el, "thumb", actor.thumb)


def _art_element(root: Element, meta: JavMetadata) -> None:
    """Add art element with poster/fanart paths."""
    art = SubElement(root, "art")
    if meta.poster_url:
        _text_element(art, "poster", meta.poster_url)


def build_nfo(meta: JavMetadata) -> str:
    """Build a complete NFO XML string from JavMetadata.

    Produces a Kodi/Emby-compatible NFO with all available fields.
    """
    root = Element("movie")

    # Title
    title = meta.full_title()
    _text_element(root, "title", title)
    _text_element(root, "originaltitle", meta.title_jp)
    _text_element(root, "sorttitle", meta.number)
    _text_element(root, "set", meta.number)

    # Identification
    _text_element(root, "id", meta.number)
    _text_element(root, "num", meta.number)
    _text_element(root, "number", meta.number)
    _text_element(root, "javid", meta.number)
    _text_element(root, "uniqueid", meta.number)
    _text_element(root, "label", meta.number)

    # Details
    _text_element(root, "rating", meta.score)
    if meta.score:
        ratings_el = SubElement(root, "ratings")
        rating_el = SubElement(ratings_el, "rating")
        _text_element(rating_el, "value", meta.score)

    _text_element(root, "year", meta.year or meta.release[:4] if meta.release else None)
    _text_element(root, "release", meta.release)
    _text_element(root, "premiered", meta.release)
    _text_element(root, "runtime", meta.runtime)
    _text_element(root, "plot", meta.plot)
    _text_element(root, "outline", meta.plot)

    # Studio hierarchy
    _text_element(root, "studio", meta.studio)
    _text_element(root, "maker", meta.maker or meta.studio)
    _text_element(root, "label", meta.label)
    _text_element(root, "publisher", meta.publisher)

    # People
    _text_element(root, "director", meta.director)
    _actors_element(root, meta)

    # Other
    _text_element(root, "mosaic", meta.mosaic)
    _text_element(root, "series", meta.series)
    _text_element(root, "source", meta.source)

    # Tags / Genres
    _genres_element(root, meta.tags)

    # Art
    _art_element(root, meta)

    # Cover
    if meta.cover_url:
        _text_element(root, "cover", meta.cover_url)
        _text_element(root, "thumb", meta.cover_url)

    # Extrafanart
    if meta.extrafanart:
        fanart_el = SubElement(root, "fanart")
        for art_url in meta.extrafanart:
            _text_element(fanart_el, "thumb", art_url)

    # Convert to pretty-printed XML string
    rough_string = tostring(root, encoding="unicode")
    dom = xml.dom.minidom.parseString(rough_string)
    return dom.toprettyxml(indent="  ")


def write_nfo(meta: JavMetadata, output_path: str) -> bool:
    """Write NFO file to disk."""
    try:
        xml_content = build_nfo(meta)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        logger.info("NFO written to %s", output_path)
        return True
    except Exception as exc:
        logger.error("Failed to write NFO: %s", exc)
        return False

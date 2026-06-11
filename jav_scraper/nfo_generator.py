"""NFO generator — Kodi/Emby/Jellyfin NFO builder.

Produces NFO format compatible with MDCx/VidHub/SenPlayer conventions.
"""

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


def _actors_element(parent: Element, meta: JavMetadata, number: str) -> None:
    """Add actor elements with role and local thumb path."""
    for actor in meta.actors:
        if actor.name:
            actor_el = SubElement(parent, "actor")
            _text_element(actor_el, "name", actor.name)
            _text_element(actor_el, "role", actor.role or actor.name)
            _text_element(actor_el, "thumb", f"{number}-poster.jpg")


def build_nfo(meta: JavMetadata) -> str:
    """Build a complete NFO XML string from JavMetadata.

    Produces a Kodi/Emby-compatible NFO with all available fields.
    Uses local file paths for media references (poster.jpg, fanart.jpg, thumb.jpg).
    """
    root = Element("movie")

    # Title — number + display title
    title = meta.full_title()
    _text_element(root, "title", title)
    _text_element(root, "sorttitle", meta.number)
    _text_element(root, "originaltitle", meta.title_jp or meta.number)

    # Set (series name, may be empty)
    _text_element(root, "set", meta.series)

    # Rating
    _text_element(root, "rating", meta.score or "0.0")

    # Year
    year = meta.year
    if not year and meta.release and len(meta.release) >= 4:
        year = meta.release[:4]
    _text_element(root, "year", year)

    # MPAA
    _text_element(root, "mpaa", "XXX")

    # Dates
    _text_element(root, "premiered", meta.release)
    _text_element(root, "release", meta.release)

    # Runtime
    _text_element(root, "runtime", meta.runtime)

    # Studio hierarchy
    _text_element(root, "studio", meta.studio or meta.maker)
    _text_element(root, "maker", meta.maker or meta.studio)
    _text_element(root, "label", meta.label or meta.studio or meta.maker)

    # Plot / Description
    plot_text = meta.plot or meta.display_title() or ""
    _text_element(root, "plot", plot_text)
    _text_element(root, "outline", plot_text)

    # Tags / Genres
    _genres_element(root, meta.tags or [])
    if not meta.tags:
        _text_element(root, "genre", "JAV")

    # Actors
    _actors_element(root, meta, meta.number)

    # Artist
    if meta.actors:
        _text_element(root, "artist", meta.actors[0].name)

    # Director
    _text_element(root, "director", meta.director)

    # Identification
    _text_element(root, "id", meta.number)
    _text_element(root, "num", meta.number)

    # Media references (local file paths for VidHub/SenPlayer)
    _text_element(root, "cover", f"{meta.number}-poster.jpg")
    _text_element(root, "poster", f"{meta.number}-poster.jpg")
    _text_element(root, "thumb", f"{meta.number}-thumb.jpg")
    _text_element(root, "fanart", f"{meta.number}-fanart.jpg")

    # Art section (for Kodi)
    art = SubElement(root, "art")
    _text_element(art, "poster", f"{meta.number}-poster.jpg")
    _text_element(art, "fanart", f"{meta.number}-fanart.jpg")

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

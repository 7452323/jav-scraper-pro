"""NFO generator — Kodi/Emby/Jellyfin NFO builder.

Produces NFO format compatible with VidHub/SenPlayer conventions.
Matches the verified working format from user's FNS-215 sample.
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
    """Add actor elements — matches working VidHub format.

    Format from working FNS-215 NFO:
      <actor>
        <name>甘夏唯</name>
        <role>Amanatsu Yui</role>   (romaji name)
        <thumb>FNS-215-poster.jpg</thumb>
      </actor>
    """
    for actor in meta.actors:
        if actor.name:
            actor_el = SubElement(parent, "actor")
            _text_element(actor_el, "name", actor.name)
            # Role: use romaji name if available, else fallback
            role = actor.role if actor.role and actor.role != "actor" else actor.name
            _text_element(actor_el, "role", role)
            _text_element(actor_el, "thumb", f"{number}-poster.jpg")


def build_nfo(meta: JavMetadata) -> str:
    """Build a VidHub-compatible NFO XML string.

    Matches the verified working format from user's FNS-215 sample.
    """
    root = Element("movie")

    num = meta.number

    # Title: "番号 日语标题" (same as working FNS-215 format)
    title_text = f"{num} {meta.title_jp}" if meta.title_jp else num
    _text_element(root, "title", title_text)
    _text_element(root, "sorttitle", num)

    # originaltitle = just the number (NOT the JP title)
    _text_element(root, "originaltitle", num)

    # Set (always present, empty like working sample)
    set_el = SubElement(root, "set")
    set_el.text = ""

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
    _text_element(root, "studio", meta.studio or meta.maker or "FALENO")
    _text_element(root, "maker", meta.maker or meta.studio or "FALENO")
    _text_element(root, "label", meta.label or meta.studio or meta.maker or "FALENO")

    # Plot = same as title (working format)
    plot_text = f"{num} {meta.title_jp}" if meta.title_jp else num
    _text_element(root, "plot", plot_text)
    _text_element(root, "outline", plot_text)

    # Genres — minimal like working sample
    # Always add JAV + Censored/Uncensored
    _text_element(root, "genre", "JAV")
    _text_element(root, "genre", meta.mosaic or "Censored")

    # Actors
    _actors_element(root, meta, num)

    # Artist (first actor)
    if meta.actors:
        _text_element(root, "artist", meta.actors[0].name)

    # Director (only if present — working sample doesn't have it)
    if meta.director:
        _text_element(root, "director", meta.director)

    # Identification
    _text_element(root, "id", num)
    _text_element(root, "num", num)

    # Media references
    _text_element(root, "cover", f"{num}-poster.jpg")
    _text_element(root, "poster", f"{num}-poster.jpg")
    _text_element(root, "thumb", f"{num}-thumb.jpg")
    _text_element(root, "fanart", f"{num}-fanart.jpg")

    # Convert to XML string with proper declaration
    rough_string = tostring(root, encoding="unicode")
    dom = xml.dom.minidom.parseString(rough_string)
    xml_str = dom.toprettyxml(indent="  ")
    # Use exact declaration matching working FNS-215 sample
    xml_str = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n' + '\n'.join(xml_str.split('\n')[1:])
    return xml_str


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

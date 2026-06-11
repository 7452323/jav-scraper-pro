"""Orchestrator — multi-source scrape, merge, and fallback."""

import logging
from typing import Callable

from jav_scraper.metadata import JavMetadata
from jav_scraper.sources import SOURCES

logger = logging.getLogger(__name__)


def _merge_metadata(
    primary: JavMetadata, secondary: JavMetadata
) -> JavMetadata:
    """Merge secondary metadata into primary, filling in missing fields."""
    merged = JavMetadata(
        number=primary.number or secondary.number,
        source=primary.source or secondary.source,
    )

    # Titles: prefer primary, fall back to secondary
    merged.title_jp = primary.title_jp or secondary.title_jp
    merged.title_cn = primary.title_cn or secondary.title_cn
    merged.title_en = primary.title_en or secondary.title_en

    # Actors: combine both, deduplicate by name
    seen_names = set()
    for a in primary.actors + secondary.actors:
        if a.name and a.name not in seen_names:
            seen_names.add(a.name)
            from jav_scraper.metadata import Actor
            merged.actors.append(Actor(name=a.name, role=a.role or "actor", thumb=a.thumb))

    # Simple fields: primary > secondary
    merged.director = primary.director or secondary.director
    merged.release = primary.release or secondary.release
    merged.year = primary.year or secondary.year
    merged.runtime = primary.runtime or secondary.runtime
    merged.score = primary.score or secondary.score
    merged.studio = primary.studio or secondary.studio
    merged.maker = primary.maker or secondary.maker
    merged.label = primary.label or secondary.label
    merged.publisher = primary.publisher or secondary.publisher
    merged.series = primary.series or secondary.series
    merged.mosaic = primary.mosaic or secondary.mosaic
    merged.plot = primary.plot or secondary.plot
    merged.cover_url = primary.cover_url or secondary.cover_url
    merged.poster_url = primary.poster_url or secondary.poster_url
    merged.trailer_url = primary.trailer_url or secondary.trailer_url
    merged.image_cut = primary.image_cut or secondary.image_cut

    # Tags / Genres: combine, deduplicate
    tags_set = set(primary.tags) | set(secondary.tags)
    merged.tags = sorted(tags_set)

    # Extrafanart: combine, deduplicate
    art_set = set(primary.extrafanart) | set(secondary.extrafanart)
    merged.extrafanart = sorted(art_set)

    return merged


def _import_source_func(func) -> Callable:
    """Ensure the function is imported and callable."""
    if callable(func):
        return func
    raise TypeError(f"Source function is not callable: {func}")


def scrape_all(number: str) -> list[tuple[str, JavMetadata | None]]:
    """Run all registered scrapers and return results."""
    results: list[tuple[str, JavMetadata | None]] = []
    for name, func, _priority in SOURCES:
        try:
            scraper = _import_source_func(func)
            meta = scraper(number)
            if meta is not None:
                meta.source = name
            results.append((name, meta))
            logger.info("Source %s returned %s", name, "data" if meta else "None")
        except Exception as exc:
            logger.warning("Source %s failed for %s: %s", name, number, exc)
            results.append((name, None))
    return results


def scrape_with_fallback(
    number: str, max_sources: int | None = None
) -> JavMetadata | None:
    """Scrape from sources in priority order, falling back until data found."""
    sorted_sources = sorted(SOURCES, key=lambda x: x[2])

    if max_sources:
        sorted_sources = sorted_sources[:max_sources]

    for name, func, _priority in sorted_sources:
        try:
            scraper = _import_source_func(func)
            meta = scraper(number)
            if meta is not None:
                meta.source = name
                logger.info("Got data from %s for %s", name, number)
                return meta
        except Exception as exc:
            logger.warning("Source %s failed for %s: %s", name, number, exc)
            continue

    logger.warning("No source found data for %s", number)
    return None


def scrape_merge(
    number: str, max_sources: int | None = None
) -> JavMetadata | None:
    """Scrape from all sources and merge results."""
    sorted_sources = sorted(SOURCES, key=lambda x: x[2])

    if max_sources:
        sorted_sources = sorted_sources[:max_sources]

    results: list[JavMetadata] = []
    for name, func, _priority in sorted_sources:
        try:
            scraper = _import_source_func(func)
            meta = scraper(number)
            if meta is not None:
                meta.source = name
                results.append(meta)
        except Exception as exc:
            logger.warning("Source %s failed for %s: %s", name, number, exc)
            continue

    if not results:
        return None

    # Start with the first result and merge in the rest
    merged = results[0]
    for other in results[1:]:
        merged = _merge_metadata(merged, other)

    # Merge source names
    merged.source = "+".join(m.source for m in results)

    return merged


def get_enabled_sources() -> list[tuple[str, Callable, int]]:
    """Return the list of registered sources."""
    return list(SOURCES)

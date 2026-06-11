"""JAV source scrapers registry.

Each source module exports a `scrape(number: str) -> JavMetadata | None` function.
Sources are ordered by priority (lower number = higher priority when merging).
"""

from typing import Callable

from jav_scraper.metadata import JavMetadata

# Each scraper function takes (number: str) -> JavMetadata | None
SourceFunc = Callable[..., JavMetadata | None]

# Priority-ordered source list: (name, scraper_func, priority)
# Lower priority number = higher priority when merging
SOURCES: list[tuple[str, SourceFunc, int]] = []


def _register(name: str, priority: int) -> None:
    """Import and register a source module."""
    import importlib

    mod = importlib.import_module(f"jav_scraper.sources.{name}")
    if hasattr(mod, "scrape") and callable(mod.scrape):
        SOURCES.append((name, mod.scrape, priority))


# --- Existing sources (priority 1-7) ---
_register("javbus", 1)
_register("javdb", 2)
_register("javlibrary", 3)
_register("avsox", 4)
_register("avsex", 5)
_register("onejav", 6)
_register("faleno", 7)

# --- New sources (priority 8-33) ---
_register("jav321", 8)
_register("mgstage", 9)
_register("prestige", 10)
_register("fc2", 11)
_register("fc2ppvdb", 12)
_register("fc2club", 13)
_register("theporndb", 14)
_register("javday", 15)
_register("airav", 16)
_register("cableav", 17)
_register("cnmdb", 18)
_register("dahlia", 19)
_register("fantastica", 20)
_register("freejavbt", 21)
_register("giga", 22)
_register("xcity", 23)
_register("kin8", 24)
_register("love6", 25)
_register("lulubar", 26)
_register("madouqu", 27)
_register("mmtv", 28)
_register("hdouban", 29)
_register("hscangku", 30)
_register("mywife", 31)
_register("official", 32)

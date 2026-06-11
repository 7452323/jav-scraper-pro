"""JAV source scrapers registry."""

from typing import Callable
from jav_scraper.metadata import JavMetadata

# Each scraper function takes (number: str) -> JavMetadata | None
SourceFunc = Callable[..., JavMetadata | None]

# Priority-ordered source list: (name, scraper_func, priority)
# Lower priority number = higher priority when merging
SOURCES: list[tuple[str, SourceFunc, int]] = []

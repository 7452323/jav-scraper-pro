"""JAV metadata data model."""

from dataclasses import dataclass, field


@dataclass
class Actor:
    name: str = ""
    role: str = ""
    thumb: str = ""


@dataclass
class JavMetadata:
    """Unified metadata model for JAV videos."""

    # Identification
    number: str = ""              # FNS-215

    # Titles in different languages
    title_jp: str = ""            # Japanese title (from source)
    title_cn: str = ""            # Chinese title (translated)
    title_en: str = ""            # English title (from some sources)

    # People
    actors: list[Actor] = field(default_factory=list)
    director: str = ""

    # Dates
    release: str = ""             # 2026-06-10
    year: str = ""

    # Technical
    runtime: str = ""             # minutes
    score: str = ""               # rating

    # Studio hierarchy
    studio: str = ""              # FALENO (片商)
    maker: str = ""               # usually same as studio
    label: str = ""               # label
    publisher: str = ""           # publisher

    # Classification
    series: str = ""
    tags: list[str] = field(default_factory=list)
    genre: list[str] = field(default_factory=list)
    mosaic: str = "Censored"

    # Description
    plot: str = ""

    # Media URLs
    cover_url: str = ""
    poster_url: str = ""
    trailer_url: str = ""
    extrafanart: list[str] = field(default_factory=list)

    # Image processing
    image_cut: str = "right"      # left/center/right

    # Source tracking
    source: str = ""

    def display_title(self) -> str:
        """Best available title: CN > JP > EN > number."""
        return self.title_cn or self.title_jp or self.title_en or self.number

    def full_title(self) -> str:
        """Full display title with number prefix."""
        title = self.display_title()
        if title.startswith(self.number):
            return title
        return f"{self.number} {title}"

    def actor_names(self) -> list[str]:
        return [a.name for a in self.actors]

    def actor_string(self) -> str:
        return ", ".join(self.actor_names())

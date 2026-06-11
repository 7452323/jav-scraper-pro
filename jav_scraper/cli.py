"""Command-line interface for JAV Scraper Pro."""

import argparse
import json
import logging
import os
import sys

from jav_scraper import __version__
from jav_scraper.metadata import JavMetadata
from jav_scraper.sources import SOURCES
from jav_scraper.orchestrator import (
    scrape_all,
    scrape_with_fallback,
    scrape_merge,
)

logger = logging.getLogger(__name__)


def _register_source(name: str, module_path: str) -> None:
    """Dynamically import and register a scraper source."""
    import importlib

    try:
        mod = importlib.import_module(module_path)
        if hasattr(mod, "scrape"):
            # Check if already registered
            for existing_name, _, _ in SOURCES:
                if existing_name == name:
                    return

            # Determine priority based on position
            priority = len(SOURCES) * 10
            SOURCES.append((name, mod.scrape, priority))
            logger.debug("Registered source: %s (%s)", name, module_path)
    except Exception as exc:
        logger.warning("Failed to register source %s: %s", name, exc)


def _register_default_sources() -> None:
    """Register all built-in scraper sources."""
    sources = [
        ("onejav", "jav_scraper.sources.onejav"),
        ("javdb", "jav_scraper.sources.javdb"),
        ("javbus", "jav_scraper.sources.javbus"),
        ("faleno", "jav_scraper.sources.faleno"),
        ("avsox", "jav_scraper.sources.avsox"),
        ("avsex", "jav_scraper.sources.avsex"),
        ("javlibrary", "jav_scraper.sources.javlibrary"),
    ]

    for name, module_path in sources:
        _register_source(name, module_path)


def _meta_to_dict(meta: JavMetadata) -> dict:
    """Convert JavMetadata to a JSON-serializable dict."""
    return {
        "number": meta.number,
        "title_jp": meta.title_jp,
        "title_cn": meta.title_cn,
        "title_en": meta.title_en,
        "actors": [
            {"name": a.name, "role": a.role, "thumb": a.thumb}
            for a in meta.actors
        ],
        "director": meta.director,
        "release": meta.release,
        "year": meta.year,
        "runtime": meta.runtime,
        "score": meta.score,
        "studio": meta.studio,
        "maker": meta.maker,
        "label": meta.label,
        "publisher": meta.publisher,
        "series": meta.series,
        "tags": meta.tags,
        "mosaic": meta.mosaic,
        "plot": meta.plot,
        "cover_url": meta.cover_url,
        "poster_url": meta.poster_url,
        "trailer_url": meta.trailer_url,
        "extrafanart": meta.extrafanart,
        "image_cut": meta.image_cut,
        "source": meta.source,
        "display_title": meta.display_title(),
        "full_title": meta.full_title(),
        "actor_string": meta.actor_string(),
    }


def cmd_scrape(args: argparse.Namespace) -> None:
    """Handle the 'scrape' subcommand."""
    _register_default_sources()

    numbers = args.number
    output_json = args.json
    translate = args.translate
    merge = args.merge

    for number in numbers:
        if merge:
            meta = scrape_merge(number)
        else:
            meta = scrape_with_fallback(number)

        if meta is None:
            msg = {"number": number, "error": "No data found from any source"}
            if output_json:
                print(json.dumps(msg, ensure_ascii=False, indent=2))
            else:
                print(f"[{number}] No data found from any source")
            continue

        # Translate if requested
        if translate:
            try:
                from jav_scraper.translator import translate_metadata

                meta = translate_metadata(meta)
            except Exception as exc:
                logger.warning("Translation failed: %s", exc)

        if output_json:
            print(json.dumps(_meta_to_dict(meta), ensure_ascii=False, indent=2))
        else:
            _print_metadata(meta)


def _print_metadata(meta: JavMetadata) -> None:
    """Print metadata in human-readable format."""
    print(f"Number:      {meta.number}")
    print(f"Source:      {meta.source}")
    print(f"Title (JP):  {meta.title_jp}")
    if meta.title_cn:
        print(f"Title (CN):  {meta.title_cn}")
    if meta.title_en:
        print(f"Title (EN):  {meta.title_en}")
    print(f"Display:     {meta.display_title()}")
    print(f"Full Title:  {meta.full_title()}")
    print(f"Actors:      {meta.actor_string()}")
    if meta.director:
        print(f"Director:    {meta.director}")
    print(f"Release:     {meta.release}")
    if meta.year:
        print(f"Year:        {meta.year}")
    print(f"Runtime:     {meta.runtime} min")
    print(f"Score:       {meta.score}")
    print(f"Studio:      {meta.studio}")
    if meta.maker:
        print(f"Maker:       {meta.maker}")
    if meta.label:
        print(f"Label:       {meta.label}")
    if meta.series:
        print(f"Series:      {meta.series}")
    print(f"Mosaic:      {meta.mosaic}")
    if meta.tags:
        print(f"Tags:        {', '.join(meta.tags)}")
    if meta.plot:
        print(f"Plot:        {meta.plot[:200]}...")
    print(f"Cover URL:   {meta.cover_url}")
    print(f"Poster URL:  {meta.poster_url}")
    print()


def cmd_nfo(args: argparse.Namespace) -> None:
    """Handle the 'nfo' subcommand."""
    _register_default_sources()

    from jav_scraper.nfo_generator import write_nfo

    number = args.number[0]
    output = args.output or f"{number}.nfo"
    translate = args.translate

    meta = scrape_merge(number) if args.merge else scrape_with_fallback(number)
    if meta is None:
        print(f"Error: No data found for {number}")
        sys.exit(1)

    if translate:
        try:
            from jav_scraper.translator import translate_metadata
            meta = translate_metadata(meta)
        except Exception as exc:
            logger.warning("Translation failed: %s", exc)

    write_nfo(meta, output)
    print(f"NFO written to {output}")


def cmd_sources(args: argparse.Namespace) -> None:
    """List registered sources."""
    _register_default_sources()
    if not SOURCES:
        print("No sources registered.")
        return

    print(f"{'#':<4} {'Name':<15} {'Priority':<10}")
    print("-" * 35)
    for i, (name, func, priority) in enumerate(SOURCES, 1):
        func_name = getattr(func, "__name__", str(func))
        print(f"{i:<4} {name:<15} {priority:<10} ({func_name})")
    print(f"\nTotal: {len(SOURCES)} source(s)")


def cmd_translate(args: argparse.Namespace) -> None:
    """Translate a title using multi-engine fallback."""
    from jav_scraper.translator import translate_title

    title = args.title
    result = translate_title(title)
    print(result)


def cmd_image(args: argparse.Namespace) -> None:
    """Process images (poster/fanart/thumb)."""
    from jav_scraper.image_processor import (
        generate_poster,
        generate_fanart,
        generate_thumb,
    )

    cover_url = args.url
    output = args.output
    image_type = args.type

    if image_type == "poster":
        success = generate_poster(cover_url, output, cut=args.cut)
    elif image_type == "fanart":
        success = generate_fanart(cover_url, output, blur=args.blur)
    elif image_type == "thumb":
        success = generate_thumb(cover_url, output)
    else:
        print(f"Unknown image type: {image_type}")
        sys.exit(1)

    if success:
        print(f"{image_type.capitalize()} saved to {output}")
    else:
        print(f"Failed to generate {image_type}")
        sys.exit(1)


def cmd_video(args: argparse.Namespace) -> None:
    """Extract video screenshots."""
    from jav_scraper.video_processor import (
        extract_screenshot,
        extract_screenshots_grid,
    )

    video = args.video
    output = args.output

    if args.grid:
        success = extract_screenshots_grid(video, output)
    else:
        success = extract_screenshot(video, output, time_sec=args.time)

    if success:
        print(f"Screenshot saved to {output}")
    else:
        print("Failed to extract screenshot")
        sys.exit(1)


def cmd_scan(args: argparse.Namespace) -> None:
    """Handle the 'scan' subcommand — batch directory scanning."""
    _register_default_sources()

    from jav_scraper.scanner import scan_directory

    directory = args.directory
    translate = args.translate
    merge = args.merge
    video_shots = not args.no_video
    recursive = not args.no_recursive

    print(f"Scanning: {directory}")
    print(f"Translate: {'yes' if translate else 'no'}")
    print(f"Merge sources: {'yes' if merge else 'no'}")
    print(f"Video screenshots: {'yes' if video_shots else 'no'}")
    print(f"Recursive: {'yes' if recursive else 'no'}")
    print()

    results = scan_directory(
        directory=directory,
        translate=translate,
        merge=merge,
        video_shots=video_shots,
        recursive=recursive,
    )

    # Print summary
    success_count = sum(1 for r in results.values() if r.get("success"))
    fail_count = sum(1 for r in results.values() if not r.get("success"))

    print()
    print("=" * 60)
    print(f"Scan complete: {success_count} success, {fail_count} failed, {len(results)} total")
    print("=" * 60)

    if args.json:
        output = {
            "directory": directory,
            "total": len(results),
            "success": success_count,
            "failed": fail_count,
            "results": {
                num: {
                    "success": r.get("success", False),
                    "nfo_path": r.get("nfo_path"),
                    "title": r.get("title"),
                    "error": r.get("error"),
                    "video_count": r.get("video_count"),
                }
                for num, r in sorted(results.items())
            },
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="jav-scraper",
        description="JAV Scraper Pro - Multi-source JAV metadata scraper",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable debug logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # scrape
    p_scrape = subparsers.add_parser("scrape", help="Scrape a JAV number")
    p_scrape.add_argument(
        "number", nargs="+", help="JAV number(s) to scrape (e.g. FNS-215)"
    )
    p_scrape.add_argument(
        "--json", "-j", action="store_true", help="Output as JSON"
    )
    p_scrape.add_argument(
        "--translate", "-t", action="store_true",
        help="Translate titles via multi-engine (free)"
    )
    p_scrape.add_argument(
        "--merge", "-m", action="store_true",
        help="Merge results from all sources"
    )

    # nfo
    p_nfo = subparsers.add_parser("nfo", help="Generate NFO file")
    p_nfo.add_argument("number", nargs=1, help="JAV number")
    p_nfo.add_argument("--output", "-o", help="Output NFO path")
    p_nfo.add_argument(
        "--translate", "-t", action="store_true",
        help="Translate titles"
    )
    p_nfo.add_argument(
        "--merge", "-m", action="store_true",
        help="Merge from all sources"
    )

    # sources
    p_sources = subparsers.add_parser(
        "sources", help="List registered sources"
    )

    # scan -- NEW!
    p_scan = subparsers.add_parser(
        "scan", help="Batch scan directory for JAV videos"
    )
    p_scan.add_argument(
        "directory", help="Directory to scan for video files"
    )
    p_scan.add_argument(
        "--translate", "-t", action="store_true",
        help="Translate titles (multi-engine fallback)"
    )
    p_scan.add_argument(
        "--merge", "-m", action="store_true",
        help="Merge from all sources"
    )
    p_scan.add_argument(
        "--no-video", action="store_true",
        help="Skip video screenshot extraction"
    )
    p_scan.add_argument(
        "--no-recursive", action="store_true",
        help="Don't scan subdirectories"
    )
    p_scan.add_argument(
        "--json", "-j", action="store_true",
        help="Output results as JSON"
    )

    # translate
    p_translate = subparsers.add_parser(
        "translate", help="Translate a title"
    )
    p_translate.add_argument("title", help="Japanese title to translate")
    p_translate.add_argument(
        "--target", "-t", default="chinese",
        choices=["chinese", "english"],
        help="Target language",
    )

    # image
    p_image = subparsers.add_parser("image", help="Process images")
    p_image.add_argument(
        "type", choices=["poster", "fanart", "thumb"],
        help="Image type"
    )
    p_image.add_argument("--url", "-u", required=True, help="Cover URL")
    p_image.add_argument("--output", "-o", required=True, help="Output path")
    p_image.add_argument(
        "--cut", default="right", choices=["left", "right", "center"],
        help="Crop side for poster (default: right)"
    )
    p_image.add_argument(
        "--blur", action="store_true",
        help="Apply blur for fanart background"
    )

    # video
    p_video = subparsers.add_parser("video", help="Video screenshots")
    p_video.add_argument("video", help="Path to video file")
    p_video.add_argument("--output", "-o", required=True, help="Output path")
    p_video.add_argument(
        "--time", type=float, default=30.0,
        help="Time offset in seconds (default: 30)"
    )
    p_video.add_argument(
        "--grid", action="store_true",
        help="Extract grid of screenshots"
    )

    return parser


def main() -> None:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="[%(levelname)s] %(name)s: %(message)s",
        )

    if args.command == "scrape":
        cmd_scrape(args)
    elif args.command == "nfo":
        cmd_nfo(args)
    elif args.command == "sources":
        cmd_sources(args)
    elif args.command == "scan":
        cmd_scan(args)
    elif args.command == "translate":
        cmd_translate(args)
    elif args.command == "image":
        cmd_image(args)
    elif args.command == "video":
        cmd_video(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

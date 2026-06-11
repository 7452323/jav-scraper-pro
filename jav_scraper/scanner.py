"""Batch directory scanner — auto-detect videos, extract JAV numbers, scrape all."""

import logging
import os
import re
from pathlib import Path

from jav_scraper.nfo_generator import write_nfo
from jav_scraper.image_processor import generate_poster, generate_fanart, generate_thumb
from jav_scraper.video_processor import extract_screenshot

logger = logging.getLogger(__name__)

# Video file extensions to scan
VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".wmv", ".mov",
    ".m4v", ".ts", ".webm", ".flv", ".mpeg",
    ".mpg", ".vob", ".3gp",
}

# JAV number patterns (ordered by specificity)
JAV_PATTERNS = [
    # FC2: FC2-123456 or FC2-1234567
    re.compile(r'(FC2[-_]?\d{6,7})', re.IGNORECASE),
    # HEYZO: HEYZO-1234
    re.compile(r'(HEYZO[-_]?\d{4})', re.IGNORECASE),
    # 1pondo / Caribbean: 061115_001
    re.compile(r'(\d{6}[-_]\d{3})'),
    # 10musume / Pacopacomama: 061115_01
    re.compile(r'(\d{6}[-_]\d{2})'),
    # Standard JAV: AAA-12345 (letter prefix + number, 2-6 letter prefix)
    re.compile(r'([A-Za-z]{2,6}[-_]?\d{2,5})'),
    # Numbers with prefix separated by underscore: ABC_12345
    re.compile(r'([A-Za-z]{2,6}_\d{2,5})'),
]


def find_video_files(directory: str, recursive: bool = True) -> list[str]:
    """Find all video files in a directory.

    Args:
        directory: Path to scan.
        recursive: Whether to scan subdirectories.

    Returns:
        List of full paths to video files.
    """
    video_files = []
    root_path = Path(directory).expanduser().resolve()

    if not root_path.is_dir():
        logger.error("Directory not found: %s", root_path)
        return []

    if recursive:
        iterator = root_path.rglob("*")
    else:
        iterator = root_path.iterdir()

    for f in sorted(iterator):
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS:
            video_files.append(str(f))

    return video_files


def extract_jav_number(filename: str) -> str | None:
    """Extract JAV number from a filename using regex patterns.

    Tries specific patterns first, falls back to generic.

    Args:
        filename: Just the filename (not full path), e.g. 'FNS-215.mp4'

    Returns:
        Standardized JAV number (uppercase, with hyphen), or None.
    """
    stem = Path(filename).stem  # remove extension

    for pattern in JAV_PATTERNS:
        m = pattern.search(stem)
        if m:
            raw = m.group(1)
            # Normalize: replace underscore with hyphen, uppercase
            normalized = raw.replace("_", "-").upper()
            # Validate: should have both letters and digits
            if re.search(r'[A-Z]', normalized) and re.search(r'\d', normalized):
                return normalized
            if normalized.startswith("FC2"):
                return normalized
            # For pure number patterns (like 1pondo)
            if re.match(r'^\d{6}-\d{2,3}$', normalized):
                return normalized

    return None


def group_videos_by_number(video_files: list[str]) -> dict[str, list[str]]:
    """Group video files by their extracted JAV number.

    Returns:
        Dict mapping JAV number -> list of video file paths.
    """
    groups: dict[str, list[str]] = {}
    for video_path in video_files:
        filename = os.path.basename(video_path)
        number = extract_jav_number(filename)
        if number:
            if number not in groups:
                groups[number] = []
            groups[number].append(video_path)
        else:
            logger.debug("Could not extract JAV number from: %s", filename)

    return groups


def scan_directory(
    directory: str,
    translate: bool = False,
    merge: bool = False,
    video_shots: bool = True,
    scrape_func=None,
    recursive: bool = True,
) -> dict[str, dict]:
    """Scan a directory, scrape all JAV videos, and output files.

    Args:
        directory: Path to scan.
        translate: Whether to translate titles.
        merge: Whether to merge from all sources.
        video_shots: Whether to extract video screenshots.
        scrape_func: Function that takes (number) -> JavMetadata | None.
                     Default: uses scrape_with_fallback (or scrape_merge if merge=True).
        recursive: Whether to scan subdirectories.

    Returns:
        Dict mapping JAV number -> result dict with 'success', 'nfo_path', 'error', etc.
    """
    from jav_scraper.orchestrator import scrape_merge, scrape_with_fallback
    from jav_scraper.translator import translate_metadata

    video_files = find_video_files(directory, recursive=recursive)
    if not video_files:
        logger.warning("No video files found in %s", directory)
        return {}

    logger.info("Found %d video files", len(video_files))

    groups = group_videos_by_number(video_files)
    logger.info("Detected %d unique JAV numbers", len(groups))

    if not groups:
        logger.warning("No JAV numbers could be extracted from any filename")
        return {}

    results = {}

    for number, video_paths in sorted(groups.items()):
        logger.info("Processing %s (%d video(s))...", number, len(video_paths))

        try:
            # Scrape
            if merge:
                meta = scrape_merge(number)
            else:
                meta = scrape_with_fallback(number)

            if meta is None:
                logger.warning("No metadata found for %s, skipping", number)
                results[number] = {"success": False, "error": "No data from any source"}
                continue

            # Translate
            if translate:
                try:
                    meta = translate_metadata(meta)
                except Exception as e:
                    logger.warning("Translation failed for %s: %s", number, e)

            # Use the directory of the first video as output dir
            output_dir = os.path.dirname(video_paths[0])
            if not output_dir:
                output_dir = "."

            # Write NFO
            nfo_path = os.path.join(output_dir, f"{number}.nfo")
            write_nfo(meta, nfo_path)

            # Download cover & generate images
            if meta.cover_url:
                try:
                    poster_path = os.path.join(output_dir, f"{number}-poster.jpg")
                    generate_poster(meta.cover_url, poster_path, cut=meta.image_cut or "right")

                    fanart_path = os.path.join(output_dir, f"{number}-fanart.jpg")
                    generate_fanart(meta.cover_url, fanart_path, blur=True)

                    thumb_path = os.path.join(output_dir, f"{number}-thumb.jpg")
                    generate_thumb(meta.cover_url, thumb_path)

                    # Also save raw cover
                    cover_path = os.path.join(output_dir, f"{number}.jpg")
                    from jav_scraper.http_client import fetch_bytes
                    raw_data = fetch_bytes(meta.cover_url)
                    if raw_data:
                        with open(cover_path, "wb") as f:
                            f.write(raw_data)
                except Exception as e:
                    logger.warning("Image generation failed for %s: %s", number, e)

            # Video screenshots (from the first/largest video)
            if video_shots and video_paths:
                # Pick the largest video file for screenshots
                largest_video = max(video_paths, key=lambda p: os.path.getsize(p))
                try:
                    for i, time_pct in enumerate([0.25, 0.50, 0.75], 1):
                        # Get duration first
                        from jav_scraper.video_processor import get_video_duration
                        duration = get_video_duration(largest_video)
                        if duration and duration > 10:
                            time_sec = duration * time_pct
                            shot_path = os.path.join(
                                output_dir, f"{number}_screenshot_{i}.jpg"
                            )
                            extract_screenshot(largest_video, shot_path, time_sec=time_sec)
                        else:
                            # Fallback: fixed timestamps
                            shot_time = {1: 30, 2: 60, 3: 90}.get(i, 30)
                            shot_path = os.path.join(
                                output_dir, f"{number}_screenshot_{i}.jpg"
                            )
                            extract_screenshot(largest_video, shot_path, time_sec=shot_time)
                except Exception as e:
                    logger.warning("Screenshot extraction failed for %s: %s", number, e)

            results[number] = {
                "success": True,
                "nfo_path": nfo_path,
                "video_count": len(video_paths),
                "title": meta.display_title(),
            }

            logger.info("✅ %s: %s", number, meta.display_title())

        except Exception as e:
            logger.error("Failed to process %s: %s", number, e)
            results[number] = {"success": False, "error": str(e)}

    return results

"""Video processor — ffmpeg screenshot extraction."""

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def get_ffmpeg_path() -> str:
    """Return ffmpeg binary path. Checks common locations."""
    candidates = ["ffmpeg", "/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"]
    for cmd in candidates:
        try:
            subprocess.run(
                [cmd, "-version"],
                capture_output=True,
                timeout=5,
            )
            return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return "ffmpeg"


def extract_screenshot(
    video_path: str,
    output_path: str,
    time_sec: float = 30.0,
    width: int = 1280,
) -> bool:
    """Extract a single screenshot from a video at the given time.

    Args:
        video_path: Path to the video file.
        output_path: Where to save the screenshot.
        time_sec: Time offset in seconds (default: 30s in).
        width: Output image width (default: 1280).

    Returns:
        True on success, False on failure.
    """
    if not os.path.isfile(video_path):
        logger.error("Video file not found: %s", video_path)
        return False

    ffmpeg = get_ffmpeg_path()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    cmd = [
        ffmpeg,
        "-y",
        "-ss", str(time_sec),
        "-i", video_path,
        "-vframes", "1",
        "-vf", f"scale={width}:-1",
        output_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            logger.warning(
                "ffmpeg screenshot failed: %s", result.stderr[:500]
            )
            return False
        logger.info("Screenshot saved to %s", output_path)
        return True
    except FileNotFoundError:
        logger.error("ffmpeg not found. Install ffmpeg.")
        return False
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg timed out")
        return False


def extract_screenshots_grid(
    video_path: str,
    output_path: str,
    num_shots: int = 6,
    width: int = 320,
) -> bool:
    """Extract multiple screenshots arranged in a grid/montage.

    Shots are evenly spaced throughout the video (skipping the first 10%
    and last 10%).
    """
    if not os.path.isfile(video_path):
        logger.error("Video file not found: %s", video_path)
        return False

    ffmpeg = get_ffmpeg_path()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # First get video duration
    duration_cmd = [
        ffmpeg,
        "-i", video_path,
        "-f", "null",
        "-",
    ]
    try:
        result = subprocess.run(
            duration_cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Parse duration from stderr
        import re
        dur_match = re.search(
            r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)",
            result.stderr,
        )
        if not dur_match:
            logger.warning("Could not determine video duration")
            return False

        total_sec = (
            int(dur_match.group(1)) * 3600
            + int(dur_match.group(2)) * 60
            + int(dur_match.group(3))
        )
    except Exception as exc:
        logger.warning("Failed to get duration: %s", exc)
        return False

    if total_sec < 10:
        logger.warning("Video too short for grid: %ds", total_sec)
        return False

    # Calculate evenly spaced timestamps (skip first/last 10%)
    start = total_sec * 0.1
    end = total_sec * 0.9
    step = (end - start) / num_shots

    timestamps = [start + step * i for i in range(num_shots)]

    # Build filter_complex for grid
    select_filter = "+".join(
        f"eq(n\\,{int(t * 30)})" for t in timestamps
    )
    cols = min(num_shots, 3)
    rows = (num_shots + cols - 1) // cols

    cmd = [
        ffmpeg,
        "-y",
        "-i", video_path,
        "-vf",
        (
            f"select='{select_filter}',"
            f"setpts=N/FRAME_RATE/TB,"
            f"scale={width}:-1,"
            f"tile={cols}x{rows}"
        ),
        "-frames:v", "1",
        output_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            logger.warning(
                "ffmpeg grid failed: %s", result.stderr[:500]
            )
            return False
        logger.info("Screenshots grid saved to %s", output_path)
        return True
    except FileNotFoundError:
        logger.error("ffmpeg not found")
        return False
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg timed out")
        return False


def get_video_duration(video_path: str) -> float | None:
    """Get video duration in seconds using ffprobe."""
    if not os.path.isfile(video_path):
        return None

    # Try ffprobe first
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except (FileNotFoundError, ValueError, subprocess.TimeoutExpired):
        pass

    # Fall back to ffmpeg
    try:
        import re
        result = subprocess.run(
            ["ffmpeg", "-i", video_path, "-f", "null", "-"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        match = re.search(
            r"Duration:\s*(\d+):(\d+):(\d+)\.\d+",
            result.stderr,
        )
        if match:
            h, m, s = map(int, match.groups())
            return float(h * 3600 + m * 60 + s)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None

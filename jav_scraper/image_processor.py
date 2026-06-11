"""Image processor — poster, fanart, thumbnail generation."""

import io
import logging
import os

from jav_scraper.http_client import fetch_bytes

logger = logging.getLogger(__name__)

# Prevent Pillow import errors from crashing
try:
    from PIL import Image, ImageFilter

    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("Pillow not installed. Image processing disabled.")


def _download_image(url: str) -> bytes | None:
    """Download an image from a URL."""
    if not url:
        return None
    return fetch_bytes(url)


def _open_image(data: bytes) -> "Image.Image | None":  # noqa: F821
    """Open image from bytes."""
    if not HAS_PIL:
        return None
    try:
        return Image.open(io.BytesIO(data))
    except Exception as exc:
        logger.warning("Failed to open image: %s", exc)
        return None


def _crop_cover(
    img: "Image.Image", cut: str = "right"  # noqa: F821
) -> "Image.Image | None":  # noqa: F821
    """Crop a cover image based on cut direction.

    JAV covers typically have the poster on the left and text on the right.
    'right' = keep the right half (poster), 'left' = keep left half,
    'center' = keep center portion.
    """
    if not HAS_PIL:
        return img

    w, h = img.size
    if cut == "left":
        return img.crop((0, 0, w // 2, h))
    elif cut == "right":
        return img.crop((w // 2, 0, w, h))
    elif cut == "center":
        offset = w // 4
        return img.crop((offset, 0, w - offset, h))
    return img


def generate_poster(
    cover_url: str,
    output_path: str,
    cut: str = "right",
    width: int = 400,
) -> bool:
    """Generate a poster image from a cover URL.

    Crops the cover (typically poster is in right half for JAV)
    and resizes to standard dimensions.
    """
    if not HAS_PIL:
        logger.error("Pillow required for image processing")
        return False

    data = _download_image(cover_url)
    if not data:
        return False

    img = _open_image(data)
    if not img:
        return False

    # Crop
    img = _crop_cover(img, cut)

    # Resize maintaining aspect ratio
    ratio = width / img.width
    height = int(img.height * ratio)
    img = img.resize((width, height), Image.LANCZOS)

    # Save
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, quality=92)
    logger.info("Poster saved to %s", output_path)
    return True


def generate_fanart(
    cover_url: str,
    output_path: str,
    width: int = 1920,
    blur: bool = False,
) -> bool:
    """Generate a fanart/background from the cover.

    If blur=True, creates a blurred background suitable for Kodi fanart.
    """
    if not HAS_PIL:
        logger.error("Pillow required for image processing")
        return False

    data = _download_image(cover_url)
    if not data:
        return False

    img = _open_image(data)
    if not img:
        return False

    # Resize to target width
    ratio = width / img.width
    height = int(img.height * ratio)
    img = img.resize((width, height), Image.LANCZOS)

    if blur:
        # Apply Gaussian blur for background effect
        img = img.filter(ImageFilter.GaussianBlur(radius=15))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, quality=90)
    logger.info("Fanart saved to %s", output_path)
    return True


def generate_thumb(
    cover_url: str,
    output_path: str,
    size: tuple[int, int] = (200, 300),
) -> bool:
    """Generate a thumbnail from the cover."""
    if not HAS_PIL:
        logger.error("Pillow required for image processing")
        return False

    data = _download_image(cover_url)
    if not data:
        return False

    img = _open_image(data)
    if not img:
        return False

    # Resize with black bars aspect-ratio-preserving thumbnail
    img.thumbnail(size, Image.LANCZOS)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, quality=85)
    logger.info("Thumb saved to %s", output_path)
    return True

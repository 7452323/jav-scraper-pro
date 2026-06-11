"""Multi-engine free translator with automatic fallback.

Uses only free translation services (no API keys required).
Tries translators in order, falling back to the next if one fails.

Available backends (all free):
  1. GoogleTranslator  - Most reliable, no key needed
  2. MyMemoryTranslator - Free tier (daily limit ~5000 chars without key)
  3. PonsTranslator     - Free dictionary-based
  4. GoogleTranslator (alt TLD) - Fallback with different endpoint
"""

import logging
import re

from deep_translator import GoogleTranslator, MyMemoryTranslator, PonsTranslator
from deep_translator.exceptions import (
    NotValidPayload,
    TranslationNotFound,
    TooManyRequests,
)

logger = logging.getLogger(__name__)

# Cache translator instances so we don't re-create them every call
_translator_cache = {}

# Ordered list of (name, factory_func) tuples
# Each factory returns a translator instance or raises on construction failure
_TRANSLATOR_FACTORIES = [
    ("google", lambda: GoogleTranslator(source="ja", target="zh-CN")),
    ("google-en", lambda: GoogleTranslator(source="ja", target="zh-TW")),
    ("mymemory", lambda: MyMemoryTranslator(source="ja", target="zh-CN")),
    ("pons", lambda: PonsTranslator(source="ja", target="zh-CN")),
]


def _get_translator(service: str, source: str = "ja", target: str = "zh-CN"):
    """Get or create a cached translator instance."""
    key = f"{service}:{source}→{target}"
    if key not in _translator_cache:
        for name, factory in _TRANSLATOR_FACTORIES:
            if name == service:
                try:
                    _translator_cache[key] = factory()
                except Exception as e:
                    logger.debug("Failed to init translator %s: %s", service, e)
                    return None
                break
    return _translator_cache.get(key)


def _has_japanese(text: str) -> bool:
    """Check if text contains Japanese characters (kana or kanji in JP context)."""
    # Check for Japanese kana (hiragana + katakana)
    has_kana = bool(re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text))
    if has_kana:
        return True
    # Check for common Japanese-only kanji compounds
    # (JP-specific kanji like 綺麗, 凄い, etc. — hard to detect perfectly)
    # For safety, also check if the text has mostly CJK but no Chinese-style punct
    cjk_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    if cjk_chars > 0 and not has_kana:
        # If it has Chinese characters but also Japanese-style punctuation
        has_jp_punct = bool(re.search(r'[【】『』「」・〜]', text))
        if has_jp_punct:
            return True
    return has_kana


def translate(
    text: str,
    source: str = "ja",
    target: str = "zh-CN",
    services: list[str] | None = None,
    force: bool = False,
) -> str:
    """Translate text using free services with automatic fallback.

    Args:
        text: Text to translate.
        source: Source language code (default: ja).
        target: Target language code (default: zh-CN).
        services: Ordered list of service names to try.
                  Default: all available free services.
        force: If True, skip language detection and always attempt translation.

    Returns:
        Translated text, or original text if all translations fail.
    """
    if not text or not text.strip():
        return ""

    # Skip language detection for ASCII-only text unless forced
    cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    has_jp = _has_japanese(text)

    if not force:
        if not has_jp and cn_chars == 0:
            # Pure ASCII - skip
            return text
        if not has_jp and cn_chars > len(text) * 0.4:
            # Looks like Chinese already (no kana detected)
            return text

    if services is None:
        services = [s for s, _ in _TRANSLATOR_FACTORIES]

    last_error = None
    truncate_to = min(len(text), 5000)

    for service_name in services:
        try:
            t = _get_translator(service_name, source, target)
            if t is None:
                continue

            result = t.translate(text[:truncate_to])
            if result and result.strip():
                return result.strip()
        except TooManyRequests:
            logger.debug("Translator %s: rate limited, falling back...", service_name)
            last_error = f"{service_name}: rate limited"
            continue
        except TranslationNotFound:
            logger.debug("Translator %s: translation not found, falling back...", service_name)
            last_error = f"{service_name}: not found"
            continue
        except NotValidPayload:
            logger.debug("Translator %s: invalid payload, falling back...", service_name)
            last_error = f"{service_name}: invalid"
            continue
        except Exception as e:
            logger.debug("Translator %s failed: %s", service_name, e)
            last_error = str(e)
            continue

    if last_error:
        logger.warning("All translators failed. Last error: %s", last_error)
    return text


def translate_title(title: str) -> str:
    """Translate Japanese title to Chinese."""
    return translate(title, "ja", "zh-CN")


def translate_tags(tags: list[str]) -> list[str]:
    """Translate tags to Chinese. Handles both Japanese and English tags."""
    result = []
    for tag in tags:
        if not tag:
            continue
        if _has_japanese(tag):
            translated = translate(tag, "ja", "zh-CN", force=True)
            result.append(translated if translated and translated != tag else tag)
        else:
            # English tag → translate to Chinese
            translated = translate(tag, "en", "zh-CN", force=True)
            result.append(translated if translated and translated != tag else tag)
    return result


def translate_metadata(meta) -> object:
    """Translate all text fields in-place, returning the metadata object.

    Uses multi-engine fallback: Google → MyMemory → PONS → Google (alt).
    """
    from jav_scraper.metadata import JavMetadata

    if not isinstance(meta, JavMetadata):
        return meta

    # Translate title if we have Japanese but no Chinese
    if meta.title_jp and not meta.title_cn and _has_japanese(meta.title_jp):
        meta.title_cn = translate_title(meta.title_jp)

    # Translate plot
    if meta.plot and _has_japanese(meta.plot):
        meta.plot = translate(meta.plot, "ja", "zh-CN")

    # Translate tags
    if meta.tags:
        meta.tags = translate_tags(meta.tags)

    return meta

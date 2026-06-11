"""Free Google Translate for JAV metadata. No API key needed."""

import logging
import re

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

_translator_cache = {}


def _get_translator(source="ja", target="zh-CN"):
    """Get cached GoogleTranslator instance."""
    key = f"{source}→{target}"
    if key not in _translator_cache:
        _translator_cache[key] = GoogleTranslator(source=source, target=target)
    return _translator_cache[key]


def translate(text: str, source="ja", target="zh-CN") -> str:
    """Translate text using free Google Translate."""
    if not text or not text.strip():
        return ""
    # Only skip if text has ZERO Japanese kana AND ZERO kanji (pure Chinese/English)
    has_jp_kana = bool(re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text))
    if not has_jp_kana:
        # No kana - might be Chinese or English, skip
        cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if cn_chars > len(text) * 0.3:
            return text
    try:
        t = _get_translator(source, target)
        result = t.translate(text[:5000])
        return result.strip() if result else text
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return text


def has_japanese(text: str) -> bool:
    """Check if text contains Japanese characters (kana)."""
    return bool(re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text))


def translate_title(title: str) -> str:
    """Translate Japanese title to Chinese."""
    return translate(title, "ja", "zh-CN")


def translate_plot(plot: str) -> str:
    """Translate Japanese plot/description to Chinese."""
    return translate(plot, "ja", "zh-CN")


def translate_tags(tags: list[str]) -> list[str]:
    """Translate a list of Japanese tags to Chinese."""
    result = []
    for tag in tags:
        if has_japanese(tag):
            translated = translate(tag, "ja", "zh-CN")
            result.append(translated)
        else:
            result.append(tag)
    return result


def translate_metadata(meta) -> object:
    """Translate all text fields in JavMetadata to Chinese, in-place."""
    from jav_scraper.metadata import JavMetadata

    if not isinstance(meta, JavMetadata):
        return meta

    # Translate title
    if meta.title_jp and not meta.title_cn and has_japanese(meta.title_jp):
        meta.title_cn = translate_title(meta.title_jp)

    # Translate plot
    if meta.plot and has_japanese(meta.plot):
        meta.plot = translate_plot(meta.plot)

    # Translate tags
    if meta.tags:
        meta.tags = translate_tags(meta.tags)

    return meta

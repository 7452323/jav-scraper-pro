"""DeepSeek LLM translation for JAV metadata."""

import json
import logging
import os

logger = logging.getLogger(__name__)


def _get_client():
    """Lazy-import openai to avoid dependency at module load."""
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("openai package not installed. Run: pip install openai")
        return None

    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning(
            "No DEEPSEEK_API_KEY or OPENAI_API_KEY set in environment"
        )
        return None

    base_url = os.getenv(
        "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
    )

    return OpenAI(api_key=api_key, base_url=base_url)


def translate_title(
    jp_title: str, target_lang: str = "chinese"
) -> str:
    """Translate a Japanese title to the target language using DeepSeek."""
    if not jp_title or not jp_title.strip():
        return ""

    client = _get_client()
    if not client:
        return jp_title

    lang_names = {
        "chinese": "Chinese",
        "english": "English",
        "cn": "Chinese",
        "en": "English",
    }
    lang = lang_names.get(target_lang.lower(), target_lang.capitalize())

    try:
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        prompt = (
            f"Translate the following Japanese adult video title to {lang}. "
            f"Keep the original meaning. Only return the translated text, "
            f"nothing else.\n\nTitle: {jp_title}"
        )

        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200,
        )

        translated = resp.choices[0].message.content.strip()
        return translated

    except Exception as exc:
        logger.warning("Translation failed: %s", exc)
        return jp_title


def translate_plot(
    jp_plot: str, target_lang: str = "chinese"
) -> str:
    """Translate a Japanese description/plot to target language."""
    if not jp_plot or not jp_plot.strip():
        return ""

    client = _get_client()
    if not client:
        return jp_plot

    lang_names = {
        "chinese": "Chinese",
        "english": "English",
        "cn": "Chinese",
        "en": "English",
    }
    lang = lang_names.get(target_lang.lower(), target_lang.capitalize())

    try:
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        prompt = (
            f"Translate the following Japanese adult video description to "
            f"{lang}. Keep the original tone. Only return the translated "
            f"text, nothing else.\n\nDescription: {jp_plot}"
        )

        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
        )

        translated = resp.choices[0].message.content.strip()
        return translated

    except Exception as exc:
        logger.warning("Plot translation failed: %s", exc)
        return jp_plot


def translate_metadata(
    meta: "JavMetadata",  # noqa: F821
    target_lang: str = "chinese",
) -> "JavMetadata":  # noqa: F821
    """Translate title and plot in a JavMetadata object in-place."""
    from jav_scraper.metadata import JavMetadata

    if not isinstance(meta, JavMetadata):
        return meta

    if meta.title_jp and not meta.title_cn:
        meta.title_cn = translate_title(meta.title_jp, target_lang)

    if meta.plot and target_lang.lower() in ("chinese", "cn"):
        # Only translate to CN if there's a Japanese plot
        import re

        has_japanese = bool(
            re.search(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]', meta.plot)
        )
        if has_japanese:
            translated = translate_plot(meta.plot, target_lang)
            if translated and translated != meta.plot:
                meta.plot = translated

    return meta

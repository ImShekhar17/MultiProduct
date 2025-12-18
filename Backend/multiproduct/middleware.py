import json
import logging
import hashlib
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from langdetect import detect, LangDetectException
from googletrans import Translator

logger = logging.getLogger(__name__)

TARGET_LANG_CODES = ["kn", "ta"]  # Kannada and Tamil

class LanguageTranslationMiddleware(MiddlewareMixin):
    """
    Optimized Middleware for language detection and translation.
    Implements Redis-based caching to reduce API overhead and support high load.
    """

    def process_request(self, request):
        try:
            # Only handle mutation requests with JSON payloads
            if request.method not in ("POST", "PUT", "PATCH"):
                return None

            # Only handle JSON
            if "application/json" not in request.META.get("CONTENT_TYPE", ""):
                return None

            if not request.body:
                return None

            payload = json.loads(request.body.decode("utf-8"))

            # Determine target language from URL path
            url_parts = request.path.strip("/").split("/")
            target_lang = "kn"
            if len(url_parts) >= 2:
                potential_lang = url_parts[1].lower()
                if potential_lang in TARGET_LANG_CODES:
                    target_lang = potential_lang

            # Optimized field processing
            translatable_fields = ("text", "message", "content", "description", "title", "name", "first_name", "last_name")
            
            for key in translatable_fields:
                if key in payload and isinstance(payload[key], str) and payload[key].strip():
                    text = payload[key].strip()
                    
                    # 1. Check if already in target language (fast skip)
                    try:
                        detected_lang = detect(text)
                    except LangDetectException:
                        detected_lang = "auto"

                    if detected_lang in TARGET_LANG_CODES:
                        continue

                    # 2. Cache Lookup
                    cache_key = self._get_cache_key(text, target_lang)
                    cached_translation = cache.get(cache_key)
                    
                    if cached_translation:
                        payload[key] = cached_translation
                        continue

                    # 3. Perform Translation
                    translator = Translator()
                    try:
                        translated_result = translator.translate(text, src=detected_lang, dest=target_lang)
                        translated_text = translated_result.text
                        
                        # Support high load by caching for 24 hours
                        cache.set(cache_key, translated_text, timeout=86400)
                        payload[key] = translated_text
                    except Exception as e:
                        logger.error(f"Translation API error for '{text[:50]}...': {e}")
                        # Keep original text if translation fails
                        pass

            # Update request body with translated content
            request._body = json.dumps(payload).encode("utf-8")

        except Exception as exc:
            logger.exception(f"LanguageTranslationMiddleware error: {exc}")

        return None

    @staticmethod
    def _get_cache_key(text, target_lang):
        """Generates a unique, length-safe cache key for translation strings."""
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return f"trans_{target_lang}_{text_hash}"

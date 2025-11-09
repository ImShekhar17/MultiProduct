import json
import logging
from django.utils.deprecation import MiddlewareMixin
from langdetect import detect, LangDetectException
from googletrans import Translator

logger = logging.getLogger(__name__)

TARGET_LANG_CODES = ["kn", "ta"]  # Kannada and Tamil

class LanguageTranslationMiddleware(MiddlewareMixin):
    """
    Middleware to detect language from incoming JSON request and
    translate it to Kannada if not Kannada/Tamil.
    """

    def process_request(self, request):
        try:
            # Only handle POST, PUT, PATCH
            if request.method not in ("POST", "PUT", "PATCH"):
                return None

            # Only handle JSON
            if "application/json" not in request.META.get("CONTENT_TYPE", ""):
                return None

            if not request.body:
                return None

            payload = json.loads(request.body.decode("utf-8"))

            # Determine target language from URL, e.g., /api/kn/... => kn
            url_parts = request.path.strip("/").split("/")
            if len(url_parts) < 2:
                target_lang = "kn"
            else:
                target_lang = url_parts[1].lower()
            if target_lang not in TARGET_LANG_CODES:
                target_lang = "kn"  # default to Kannada

            # Detect and translate text fields
            for key in ("text", "message", "content", "description", "title", "name", "email"):
                if key in payload and isinstance(payload[key], str) and payload[key].strip():
                    text = payload[key].strip()
                    try:
                        detected_lang = detect(text)
                    except LangDetectException:
                        detected_lang = "auto"

                    # Translate if not Kannada/Tamil
                    if detected_lang not in TARGET_LANG_CODES:
                        translator = Translator()
                        try:
                            translated_text = translator.translate(
                                text, src=detected_lang, dest=target_lang
                            ).text
                        except Exception:
                            translated_text = text
                        payload[key] = translated_text  # overwrite with translated text
                    # else: leave kn/ta as-is

            # Replace request.body so view gets translated data automatically
            request._body = json.dumps(payload).encode("utf-8")

        except Exception as exc:
            logger.exception(f"LanguageTranslationMiddleware error: {exc}")

        return None

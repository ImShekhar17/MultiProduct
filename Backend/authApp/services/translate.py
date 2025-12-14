# api/services/translate.py
from langdetect import detect, LangDetectException
from googletrans import Translator
# from authApp.models import TranslatedText
from django.contrib.contenttypes.models import ContentType

TARGET_LANGUAGE = "kn"  # translate to Kannada only

def process_text_with_translation(text: str, instance=None):
    """
    Detect language and translate to Kannada if input is not Kannada/Tamil.
    Optionally stores translations for a model instance.
    Returns dict of language_code -> translated_text
    """
    try:
        detected_lang = detect(text)
    except LangDetectException:
        detected_lang = 'auto'

    translations = {}

    # Leave Kannada and Tamil as-is
    if detected_lang in ["kn", "ta"]:
        translations[detected_lang] = text
    else:
        translator = Translator()
        try:
            translated_text = translator.translate(text, src=detected_lang, dest=TARGET_LANGUAGE).text
        except Exception:
            translated_text = ""
        translations[TARGET_LANGUAGE] = translated_text

    # Store translations in DB if instance is provided
    if instance:
        content_type = ContentType.objects.get_for_model(instance)
        for lang_code, translated_text in translations.items():
            TranslatedText.objects.create(
                content_type=content_type,
                object_id=instance.id,
                language_code=lang_code,
                translated_text=translated_text
            )

    return translations



def perform_translation(instance_id, source_lang=None):
    """
    (Called asynchronously)
    Actually performs translation and updates DB for a given TranslatedText instance.
    """
    try:
        instance = TranslatedText.objects.get(id=instance_id)
        text = getattr(instance, "original_text", None)
        if not text:
            return

        try:
            detected_lang = detect(text)
        except LangDetectException:
            detected_lang = source_lang or "auto"

        # Skip if already Kannada or Tamil
        if detected_lang in ["kn", "ta"]:
            translations = {detected_lang: text}
        else:
            translator = Translator()
            try:
                translated_text = translator.translate(text, src=detected_lang, dest=TARGET_LANGUAGE).text
            except Exception:
                translated_text = ""
            translations = {TARGET_LANGUAGE: translated_text}

        # Save translations into DB field
        instance.translations = translations
        instance.save(update_fields=["translations"])
    except Exception as e:
        import logging
        logging.exception("perform_translation failed: %s", e)

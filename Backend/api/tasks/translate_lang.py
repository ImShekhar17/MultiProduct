from celery import shared_task
from googletrans import Translator
from django.conf import settings

SUPPORTED_LANGUAGES = ['en', 'hi', 'ta', 'te', 'kn', 'ml', 'bn']  # Add more as needed

@shared_task
def translate_to_all_languages(text, source_language):
    translator = Translator()
    translations = {}
    
    for target_lang in SUPPORTED_LANGUAGES:
        if target_lang != source_language:
            try:
                translated = translator.translate(text, src=source_language, dest=target_lang)
                translations[target_lang] = translated.text
            except Exception as e:
                translations[target_lang] = f"Translation failed: {str(e)}"
    
    return translations

@shared_task
def update_translations_for_model(model_id, text_field_name):
    from api.models import TranslatedText
    
    try:
        instance = TranslatedText.objects.get(id=model_id)
        translations = translate_to_all_languages(
            getattr(instance, text_field_name),
            instance.original_language
        )
        instance.translations = translations
        instance.save()
    except Exception as e:
        return f"Translation update failed: {str(e)}"
from langdetect import detect
from .models import TranslatedText
from .tasks.translate_lang import update_translations_for_model

def process_text_with_translation(text):
    """
    Process incoming text:
    1. Detect language
    2. Store original text
    3. Queue translation task
    """
    try:
        # Detect language of incoming text
        detected_language = detect(text)
        
        # Create TranslatedText instance
        translated_text = TranslatedText.objects.create(
            original_text=text,
            original_language=detected_language,
            translations={}  # Will be populated by background task
        )
        
        # Queue translation task
        update_translations_for_model.delay(
            translated_text.id,
            'original_text'
        )
        
        return translated_text
    except Exception as e:
        raise Exception(f"Text processing failed: {str(e)}")
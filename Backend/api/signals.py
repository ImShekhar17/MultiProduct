# # api/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.apps import apps
# from django.conf import settings
# from api.models import TranslatedText
# from api.services.translate import process_text_with_translation
# from django.contrib.contenttypes.models import ContentType

# CANDIDATE_FIELDS = ('description', 'message', 'content', 'text', 'name', 'title')

# @receiver(post_save)
# def auto_translate_on_save(sender, instance, created, **kwargs):
#     # Skip TranslatedText itself
#     if sender.__name__ == 'TranslatedText':
#         return

#     # Skip during migration or system setup
#     if apps.ready is False or getattr(settings, "RUNNING_MIGRATIONS", False):
#         return

#     # Skip unmanaged or internal models
#     if not hasattr(instance, '_meta') or instance._meta.app_label in ('contenttypes', 'sessions', 'admin', 'auth', 'migrations'):
#         return

#     # Find first candidate text field
#     text = None
#     for field in CANDIDATE_FIELDS:
#         if hasattr(instance, field):
#             value = getattr(instance, field)
#             if isinstance(value, str) and value.strip():
#                 text = value.strip()
#                 break
#     if not text:
#         return

#     # Process translation and store
#     process_text_with_translation(text, instance=instance)

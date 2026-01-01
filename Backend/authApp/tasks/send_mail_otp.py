from celery import shared_task
from django.utils import timezone
from authApp.services.translate import perform_translation
from django.conf import settings
from multiproduct.config import SITE_BASE_URL, DEFAULT_FROM_EMAIL

@shared_task(name="api.tasks.translate_lang.translate_to_all_languages")
def update_translations_for_model(translated_text_id, source_lang):
    perform_translation(translated_text_id, source_lang)


@shared_task
def send_email_otp(email, otp):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags

    subject = "STARK SECURE - Verification Sequence Required"
    context = {'otp': otp}
    
    # Render HTML and Plain Text
    html_content = render_to_string('emails/otp.html', context)
    text_content = strip_tags(html_content)

    from_email = DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()



@shared_task
def send_welcome_email(email, first_name):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags

    subject = "Access Authorized - Welcome to Stark Industries"
    context = {'first_name': first_name}
    
    # Render HTML and Plain Text
    html_content = render_to_string('emails/welcome.html', context)
    text_content = strip_tags(html_content)

    from_email = DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def cleanup_expired_otps():
    """Deletes expired or already used OTPs to keep the table optimized."""
    from authApp.models import UserOTP
    
    now = timezone.now()
    # Delete OTPs that are older than 1 hour or already used
    # This keeps the table size minimal for high-performance indexing
    deleted_count, _ = UserOTP.objects.filter(
        expires_at__lt=now
    ).delete()
    
    used_deleted_count, _ = UserOTP.objects.filter(
        is_used=True
    ).delete()
    
    return f"Cleaned up {deleted_count} expired and {used_deleted_count} used OTPs."

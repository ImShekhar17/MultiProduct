from celery import shared_task
from api.services.translate import perform_translation

@shared_task(name="api.tasks.translate_lang.translate_to_all_languages")
def update_translations_for_model(translated_text_id, source_lang):
    perform_translation(translated_text_id, source_lang)


@shared_task
def send_email_otp(email, otp):
    from django.core.mail import send_mail

    subject = "Your One-Time Password (OTP) - [Bank Name]"
    
    message = f"""
Dear Customer,

We have received a request to access your account. 
Please use the following One-Time Password (OTP) to proceed:

OTP Code: {otp}

This OTP is valid for the next 10 minutes. 
Do not share this code with anyone for your security.

If you did not request this, please contact our Customer Support immediately.

Thank you for banking with us.

Best regards,
Admin Team
[Bank Name]
Email: support@[bankname].com
Phone: +91-XXXXXXXXXX
Website: www.[bankname].com

---
This email and its contents are confidential and intended solely for the recipient. 
If you received this email in error, please delete it immediately and notify us.
"""
    
    from_email = "no-reply@[bankname].com"
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

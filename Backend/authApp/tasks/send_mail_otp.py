from celery import shared_task
from authApp.services.translate import perform_translation
from django.conf import settings

@shared_task(name="api.tasks.translate_lang.translate_to_all_languages")
def update_translations_for_model(translated_text_id, source_lang):
    perform_translation(translated_text_id, source_lang)


@shared_task
def send_email_otp(email, otp):
    from django.core.mail import send_mail

    subject = "Your One-Time Password (OTP) - Kannada Bank"
    
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
Email: support@sbi.com
Phone: +91-XXXXXXXXXX
Website: www.sbi.com

---
This email and its contents are confidential and intended solely for the recipient. 
If you received this email in error, please delete it immediately and notify us.
"""
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)




@shared_task
def send_welcome_email(email, first_name):
    from django.core.mail import send_mail

    subject = "Welcome to Kannada Bank - Your Account is Ready"
    
    message = f"""
Dear {first_name},

Welcome to Kannada Bank! We are delighted to have you on board. 
Your account has been successfully registered, and you can now enjoy our secure and convenient banking services.

Here are some important details for you to get started:

- Customer Support: +91-XXXXXXXXXX
- Email Support: support@sbi.com
- Website: www.sbi.com

We recommend you keep your login credentials secure and never share them with anyone. 
For your safety, always verify the authenticity of emails and communications claiming to be from Kannada Bank.

Thank you for choosing Kannada Bank. We look forward to serving your financial needs.

Best regards,
Admin Team
Kannada Bank
Email: support@sbi.com
Phone: +91-XXXXXXXXXX
Website: www.sbi.com

---
This email and its contents are confidential and intended solely for the recipient. 
If you received this email in error, please delete it immediately and notify us.
"""
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

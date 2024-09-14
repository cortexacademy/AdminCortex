from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def send_otp_email(email: str, otp: str):
    if not settings.AWS_SES_ACCESS_KEY_ID or not settings.AWS_SES_SECRET_ACCESS_KEY:
        raise ImproperlyConfigured("AWS SES credentials are not configured properly.")

    subject = "Your OTP Code"
    context = {
        'otp': otp,
        'email': email,
    }

    html_message = render_to_string('emails/otp_email_template.html', context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,  # Fallback to plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,  # Fail loudly if something goes wrong
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

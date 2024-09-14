import os
from datetime import datetime
from rest_framework.authtoken.models import Token

from datetime import timedelta
from django.utils import timezone
from django.conf import settings


def custom_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    original_filename = os.path.splitext(filename)[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"{timestamp}_{original_filename}.{ext}"
    return os.path.join("images/", new_filename)


# this return left time
def expires_in(token):
    time_elapsed = timezone.now() - token.created
    left_time = timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
    return left_time


# token checker if token expired or not
def is_token_expired(token) -> bool:
    return expires_in(token) < timedelta(seconds=0)


# if token is expired new token will be established
# If token is expired then it will be removed
# and new one with different key will be created
def token_expire_handler(token):
    try:
        is_expired = is_token_expired(token)
        if is_expired:
            token.delete()
            token = Token.objects.create(user=token.user)
        return token, is_expired
    except Exception as e:
        return token, True


def refresh_token(token):
    try:
        token.delete()
        token = Token.objects.create(user=token.user)
        return token
    except Exception as e:
        return token
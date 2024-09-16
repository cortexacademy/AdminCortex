from admin_panel.settings import EMAIL_TOKEN_VALIDITY

from ..utils import is_token_expired
from django.contrib.auth import (
    get_user_model,
)
from rest_framework import exceptions

from rest_framework.authentication import (
    TokenAuthentication,
)


from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import DjangoModelPermissions


User = get_user_model()


class CustomTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        if is_token_expired(token):
            raise exceptions.AuthenticationFailed(_("The Token is expired"))
        return (token.user, token)


class CustomDjangoModelPermissions(DjangoModelPermissions):
    # Override the permission map to include 'view' permission for GET requests
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],  # Add 'view' permission for GET
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

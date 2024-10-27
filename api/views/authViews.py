import json
from django.http import JsonResponse

from admin_panel.settings import EMAIL_TOKEN_VALIDITY
from api.common.authentication import CustomTokenAuthentication
from api.mixins import CustomResponseMixin
from api.models import UserEmailAuth
from api.serializers import UserEmailAuthSerializer
from ..utils import refresh_token, token_expire_handler, is_token_expired
from django.core import serializers
from ..errors import error_json
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login as auth_login,
    logout as auth_logout,
)
from rest_framework import status

from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.authentication import (
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken import views
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer
from django.utils.translation import gettext_lazy as _

# --------------------------------- Models ---------------------------------

User = get_user_model()

# --------------------------------- Views ---------------------------------


class CheckEmailAvailable(APIView, CustomResponseMixin):
    def post(self, request: Request, format=None):
        body = request.data
        if body.get("email") is None:
            return self.error_response(
                message="Email is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        email: str = body.get("email")
        if User.objects.filter(email=email.lower()).exists():

            return self.error_response(
                message="Email is already taken",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return self.success_response(
                message="Email is available", status_code=status.HTTP_200_OK
            )


class SendEmailOTP(APIView, CustomResponseMixin):

    def post(self, request: Request, format=None):
        body = request.data
        if body.get("email") is None:
            return self.error_response(
                message="Email is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=(body.get("email").lower())).exists():
            return self.error_response(
                message="Email is already taken. Please use another email or Login",
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        else:
            tokenObj, created = UserEmailAuth.objects.get_or_create(
                email=body.get("email")
            )

            if not created:
                tokenObj.refresh_object()

            tokenObj.send_otp()

            serializer = UserEmailAuthSerializer(tokenObj)

            return self.success_response(
                message="OTP sent successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )


class VerifyEmailOTP(APIView, CustomResponseMixin):
    def post(self, request: Request, format=None):
        body = request.data
        if str(body.get("token")) is None:
            return self.error_response(
                message="Token is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if str(body.get("otp")) is None:
            return self.error_response(
                message="OTP is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        tokenObj = UserEmailAuth.objects.filter(token=body.get("token").strip()).first()

        if tokenObj is None:
            return self.error_response(
                message="Invalid Token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if tokenObj.verify_otp(body.get("otp")):
            serializer = UserEmailAuthSerializer(tokenObj)

            return self.success_response(
                message="OTP verified successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )

        return self.error_response(
            message="Invalid OTP",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class CreateUserView(APIView, CustomResponseMixin):
    renderer_classes = (JSONRenderer,)

    def post(self, request: Request, format=None):
        body = json.loads(request.body)

        body = request.data
        # Check for required fields
        if body.get("token") is None:
            return self.error_response(
                message="Token is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if body.get("password") is None:
            return self.error_response(
                message="Password is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if body.get("first_name") is None:
            return self.error_response(
                message="First Name is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if body.get("last_name") is None:
            return self.error_response(
                message="Last Name is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Verify token
        tokenObj = UserEmailAuth.objects.filter(token=body.get("token").strip()).first()

        if tokenObj is None:
            return self.error_response(
                message="Invalid Token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not tokenObj.is_verified:
            return self.error_response(
                message="OTP not verified",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not tokenObj.check_token():
            return self.error_response(
                message="Token expired",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        email = tokenObj.email

        try:
            # Create user
            new_user = User.objects.create_user(
                email=email,
                password=body.get("password"),
                first_name=body.get("first_name"),
                last_name=body.get("last_name"),
            )
            # Serialize new user data
            new_user_data = json.loads(serializers.serialize("json", [new_user]))[0]
            tokenObj.delete()
            auth_login(request, new_user)
            token, created = Token.objects.get_or_create(user=new_user)
            token, is_expired = token_expire_handler(token)
            return self.success_response(
                message="User created successfully",
                data={"user": new_user_data, "token": token.key},
                status_code=status.HTTP_201_CREATED,
            )

        except IntegrityError as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except ValidationError as e:
            # This could occur if the user model validation fails
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            # Generic exception handler for other unexpected errors
            return self.error_response(
                message=f"An unexpected error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginView(views.ObtainAuthToken, CustomResponseMixin):

    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user_data = json.loads(serializers.serialize("json", [user]))[0]
        auth_login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        token, is_expired = token_expire_handler(token)
        return self.success_response(
            message="Login Successfull",
            data={"user": user_data, "token": token.key},
            status_code=status.HTTP_200_OK,
        )


class ValidateLoginView(APIView, CustomResponseMixin):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, format=None):
        if request.auth is not None:
            token = refresh_token(request.auth)
        content = {
            "user": json.loads(serializers.serialize("json", [request.user]))[
                0
            ],  # `django.contrib.auth.User` instance.
            "token": str(token.key),  # None
        }
        return self.success_response(
            message="User is authenticated",
            data=content,
            status_code=status.HTTP_200_OK,
        )


@login_required(login_url="/api/auth/invalid_login/")
def logoutUser(request):
    auth_logout(request)
    return JsonResponse({"message": "Logout Successfull"}, status=200)


def invalidLogin(request):
    return JsonResponse({"message": "Unauthorized Request"}, status=400)

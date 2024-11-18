import json
from django.http import JsonResponse
from rest_framework.generics import RetrieveAPIView

from admin_panel.settings import EMAIL_TOKEN_VALIDITY, FORGOT_PASSWORD_EMAIL_TTL
from api.common.authentication import CustomTokenAuthentication
from api.mixins import AuthMixin, CustomResponseMixin
from api.models import UserDetails, UserEmailAuth, UserForgetPassword
from api.serializers import (
    UserEmailAuthSerializer,
    UserProfileSerializer,
)
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
from django.db import transaction


from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

# --------------------------------- Models ---------------------------------

User = get_user_model()

# --------------------------------- Views ---------------------------------


class CheckEmailAvailable(APIView, CustomResponseMixin):

    authentication_classes = []

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

    authentication_classes = []

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
    authentication_classes = []

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
    authentication_classes = []

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
        if body.get("city") is None:
            return self.error_response(
                message="City is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if body.get("native_state") is None:
            return self.error_response(
                message="Native State is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if body.get("college_state") is None:
            return self.error_response(
                message="College State is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if body.get("country") is None:
            return self.error_response(
                message="Country is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if body.get("pincode") is None:
            return self.error_response(
                message="Pincode is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if body.get("college_name") is None:
            return self.error_response(
                message="College Name is required in request body",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if body.get("batch_year") is None:
            return self.error_response(
                message="Batch Year is required in request body",
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
            with transaction.atomic():
                # Create user
                new_user = User.objects.create_user(
                    email=email,
                    password=body.get("password"),
                    first_name=body.get("first_name"),
                    last_name=body.get("last_name"),
                )

                # Serialize new user data
                tokenObj.delete()
                auth_login(request, new_user)
                token, created = Token.objects.get_or_create(user=new_user)
                token, is_expired = token_expire_handler(token)

                user_details = UserDetails.objects.create(
                    user=new_user,
                    city=body.get("city"),
                    native_state=body.get("native_state"),
                    college_state=body.get("college_state"),
                    country=body.get("country"),
                    pincode=body.get("pincode"),
                    college_name=body.get("college_name"),
                    batch_year=UserDetails.ProfessionalYear[body.get("batch_year")],
                )
                user_details.save()
                user = UserProfileSerializer(new_user).data

                return self.success_response(
                    message="User created successfully",
                    data={"user": user, "token": token.key},
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
        user_data = UserProfileSerializer(user).data
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
            "user": UserProfileSerializer(request.user).data,
            "token": str(token.key),  # None
        }
        return self.success_response(
            message="User is authenticated",
            data=content,
            status_code=status.HTTP_200_OK,
        )


class UserDetailsView(AuthMixin, RetrieveAPIView, CustomResponseMixin):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def get(self, request: Request):
        serializer = self.get_serializer(request.user)
        return self.success_response(
            message="User details fetched successfully", data=serializer.data
        )


class ResetPasswordView(APIView, CustomResponseMixin):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, format=None):
        print(request.user)
        user_data = UserProfileSerializer(request.user).data
        current_password = request.data.get("current_password", None)
        print(current_password)
        if not current_password:
            print("heree")
            return self.error_response("Current Password Not Provided")

        check = request.user.check_password(current_password)
        if not check:
            return self.error_response("Currect Password is Incorrect")

        password = request.data.get("password", None)
        # user_df = User.objects.get(pk=2)

        request.user.set_password(password)
        request.user.save()

        return self.success_response(data=user_data)


@login_required(login_url="/api/auth/invalid_login/")
def logoutUser(request):
    auth_logout(request)
    return JsonResponse({"message": "Logout Successfull"}, status=200)


def invalidLogin(request):
    return JsonResponse({"message": "Unauthorized Request"}, status=400)


class PasswordResetOTPEmail(APIView, CustomResponseMixin):
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request, format=None):
        email = request.data.get("email", None)
        if not email:
            return self.error_response("Email not found in body.")

        try:
            if not User.objects.filter(email=email).exists():
                return self.success_response(
                    message="If an account exists with this email, an OTP has been sent.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            forgetPassword, created = UserForgetPassword.objects.get_or_create(
                email=email
            )

            if not created:
                if (
                    forgetPassword.seconds_since_last_email()
                    < FORGOT_PASSWORD_EMAIL_TTL
                ):
                    return self.error_response(
                        "Please wait at least 15 minutes before sending another email.",
                        status_code=status.HTTP_425_TOO_EARLY,
                    )
                else:
                    forgetPassword.refresh_object()

            forgetPassword.send_otp_mail()
            return self.success_response(
                message="If an account exists with this email, a password reset link has been sent.",
                data={"token": forgetPassword.token, "otp": forgetPassword.otp},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except User.DoesNotExist:
            # For security reasons, return success even if email doesn't exist
            return Response(
                {
                    "message": "If an account exists with this email, a password reset link has been sent."
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": "Failed to send password reset email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def verifytoken(userid, token):
    return True


class PasswordResetConfirmView(APIView, CustomResponseMixin):
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request):
        # Check if token is valid
        token = request.data.get("token", None)
        otp = request.data.get("otp", None)
        password = request.data.get("password", None)

        if not password or not token or not otp:

            return self.error_response(
                message="Password or Token or OTP not present in request body."
            )

        try:
            forgetPassword = UserForgetPassword.objects.filter(token=token).first()

            if forgetPassword is not None:
                if forgetPassword.verify_otp(otp):
                    user = User.objects.filter(email=forgetPassword.email).first()
                    if not user:
                        print("No user with given email: " + forgetPassword.email)
                        return self.error_response(
                            "Unable to reset password with given OTP and token."
                        )
                    user.set_password(password)
                    user.save()
                    forgetPassword.refresh_object()
                    forgetPassword.save()
                    forgetPassword.delete()
                    return self.success_response("password updates successfully")
                else:
                    print(f"Invalid OTP: {otp} vs {forgetPassword.otp}")
                    return self.error_response(
                        "Unable to reset password with given OTP and token"
                    )

            else:
                print("No such token present")
                return self.error_response(
                    "Unable to reset password with given OTP and token"
                )

        except User.DoesNotExist as e:
            print("ERROR: " + e)
            return self.error_response(
                message="Unable to reset password with given OTP and token"
            )
        except Exception as e:
            print("Error: " + e)
            return self.error_response(
                message="Unable to reset password with given OTP and token"
            )

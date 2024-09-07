import json
from django.http import Http404, HttpResponse
from django.http import JsonResponse
from ..models import Subject
from ..utils import token_expire_handler
from django.core import serializers
from ..errors import error_json
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login as auth_login,
    logout as auth_logout,
)
from rest_framework import status

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken import views
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer

User = get_user_model()


class CreateUserView(APIView):
    renderer_classes = (JSONRenderer,)

    def post(self, request, format=None):
        body = json.loads(request.body)

        try:
            body = json.loads(request.body)
            # Check for required fields
            if body.get("email") is None:
                return error_json("400", "Email is required")
            if body.get("password") is None:
                return error_json("400", "Password is required")
            if body.get("first_name") is None:
                return error_json("400", "First Name is required")
            if body.get("last_name") is None:
                return error_json("400", "Last Name is required")
            if body.get("phone_number") is None:
                return error_json("400", "Phone Number is required")
            # Create user
            new_user = User.objects.create_user(
                email=body.get("email"),
                password=body.get("password"),
                first_name=body.get("first_name"),
                last_name=body.get("last_name"),
                phone_number=body.get("phone_number"),
            )
            # Serialize new user data
            new_user_data = json.loads(serializers.serialize("json", [new_user]))[0]
            return Response(
                {
                    "message": "User created successfully",
                    "new_user_data": new_user_data,
                },
                status=status.HTTP_201_CREATED,
            )

        except IntegrityError as e:
            print("JSON: ", e)
            return error_json("400", str(e))

        except ValidationError as e:
            # This could occur if the user model validation fails
            return error_json("400", str(e))

        except Exception as e:
            # Generic exception handler for other unexpected errors
            return error_json("500", f"An unexpected error occurred: {str(e)}")


class ValidateLoginView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            "user": json.loads(serializers.serialize("json", [request.user]))[
                0
            ],  # `django.contrib.auth.User` instance.
            "auth": str(request.auth),  # None
        }
        return Response(content)


class LoginView(views.ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user_data = json.loads(serializers.serialize("json", [user]))[0]
        print("User: ", user_data)
        auth_login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        token, is_expired = token_expire_handler(token)
        return Response(
            {"message": "Login Successfull", "body": user_data, "token": token.key},
            status=200,
        )


@login_required(login_url="/api/auth/invalid_login/")
def logoutUser(request):
    auth_logout(request)
    return JsonResponse({"message": "Logout Successfull"}, status=200)


def invalidLogin(request):
    return JsonResponse({"message": "Unauthorized Request"}, status=400)

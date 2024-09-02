import json
from django.http import Http404, HttpResponse
from django.http import JsonResponse
from ..models import Subject
from django.core import serializers
from ..errors import error_json
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login as auth_login,
    logout as auth_logout,
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


User = get_user_model()


@csrf_exempt
def createUser(request):
    body = json.loads(request.body)

    new_user = User.objects.create_user(
        email=body.get("email"),
        password=body.get("password"),
        first_name=body.get("first_name"),
        last_name=body.get("last_name"),
        phone_number=body.get("phone_number"),
    )

    new_user_data = json.loads(serializers.serialize("json", [new_user]))[0]

    return JsonResponse(
        {"message": "This is a sample response", "new_user_data": new_user_data},
        status=200,
    )


def loginUser(request):
    user = json.loads(request.body)

    if user.get("email") is None:
        return error_json("400", "Username is required")
    if user.get("password") is None:
        return error_json("400", "Password is required")

    userAuth = authenticate(
        username=user.get("email", ""), password=user.get("password", "")
    )

    if userAuth is None:
        return error_json("401", "Invalid credentials")

    auth_login(request, userAuth)
    user_data = json.loads(serializers.serialize("json", [userAuth]))[0]

    return JsonResponse({"message": "Login Successfull", "body": user_data}, status=200)


def testLogin(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {"message": "Login Successfull", "body": "user_data"}, status=200
        )
    else:
        return JsonResponse(
            {"message": "Login Failed", "body": "user_data"}, status=401
        )


@login_required(login_url="/api/auth/invalid_login/")
def logoutUser(request):
    auth_logout(request)
    return JsonResponse({"message": "Logout Successfull"}, status=200)


def invalidLogin(request):
    return JsonResponse({"message": "Unauthorized Request"}, status=400)

import json
from django.http import Http404, HttpResponse
from django.http import JsonResponse
from ..models import Subject
from django.core import serializers
from ..errors import error_json
from django.contrib.auth import authenticate
from django.contrib.auth.models import User



def createTempUser(request):
    body = json.loads(request.body)

    User.objects.create_user(username="test1",email="test@gmail.com",password="test")
    print(body)
    return JsonResponse({"message":"This is a sample response","body":body},status=200)


def login(request):
    user = json.loads(request.body)

    if user.get('username') is None:
        return error_json("400","Username is required")
    if user.get('password') is None:
        return error_json("400","Password is required")
    
    user_by_email = User.objects.filter(email=user.get('username')).values().first()

    if user_by_email is None:
        return error_json("401","Invalid credentials")

    userAuth = authenticate(username=user_by_email.get("username","") ,password=user.get("password",""))

    if userAuth is None:
        return error_json("401","Invalid credentials")
    body = json.loads(request.body)

    # print(body)
    return JsonResponse({"message":"This is a sample response","body":body},status=200)
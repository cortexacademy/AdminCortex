from django.urls import path
from api.errors import error_json
from ..views import authViews


urlpatterns = [
    path("createUser/", authViews.createUser, name="createUser"),
    path("login/", authViews.loginUser(), name="login"),
    path("test_login/", authViews.testLogin(), name="test_login"),
    path("logout/", authViews.logoutUser(), name="logout"),
    path("invalid_login/", authViews.invalidLogin(), name="invalid_login"),
]

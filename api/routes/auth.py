from django.urls import path
from api.errors import error_json
from ..views import authViews


urlpatterns = [
    path("createuser/", authViews.CreateUserView.as_view(), name="createUser"),
    path("login/", authViews.LoginView.as_view(), name="login"),
    path("validate/", authViews.ValidateLoginView.as_view(), name="test_login"),
    path("logout/", authViews.logoutUser, name="logout"),
    path("invalid_login/", authViews.invalidLogin, name="invalid_login"),
]

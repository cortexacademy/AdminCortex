from django.urls import path
from api.errors import error_json
from .views import views, authViews


authUrls = [
    path("auth/createUser/", authViews.createTempUser, name="createTempUser"),
    path("auth/login/", authViews.login_user, name="login"),
    path("auth/test_login/", authViews.test_login, name="test_login"),
    path("auth/logout/", authViews.logout_user, name="logout"),
    path("auth/invalid_login/", authViews.invalid_login, name="invalid_login"),
]

subjectUrls = [
    path("subject/<int:id>/", views.index1, name="index1"),
    path("subject/<int:id>/questions/", views.custom_view, name="custom_view"),
]

urlpatterns = (
    [
        path("", views.index, name="index"),
    ]
    + authUrls
    + subjectUrls
)

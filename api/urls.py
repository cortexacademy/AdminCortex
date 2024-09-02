from django.urls import path, include
from api.errors import error_json
from .views import subjectViews, authViews


urlpatterns = [
    path("", subjectViews.index, name="index"),
    path("auth/", include("api.routes.auth")),
    path("subject/", include("api.routes.subject")),
]

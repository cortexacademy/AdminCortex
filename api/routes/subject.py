from django.urls import path
from api.errors import error_json
from ..views import subjectViews


urlpatterns = [
    path("<int:id>/", subjectViews.index1, name="index1"),
    path("<int:id>/questions/", subjectViews.custom_view, name="custom_view"),
]

from django.urls import path
from ..views.yearViews import *

urlpatterns = [
    path("", YearsListView.as_view(), name="years-list"),
]

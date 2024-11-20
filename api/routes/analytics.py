# api/routes/exam/urls.py
from django.urls import path
from ..views.analyticsViews import AnalyticsView

urlpatterns = [
    path("", AnalyticsView.as_view(), name="exam-list"),
]

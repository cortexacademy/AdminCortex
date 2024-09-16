from django.urls import path
from ..views.questionViews import *

urlpatterns = [
    path("", QuestionListView.as_view(), name="question-list"),
    path("<int:id>/", QuestionDetailView.as_view(), name="question-detail"),
]

from django.urls import path
from ..views.dailyQuestionViews import DailyQuestionListView

urlpatterns = [
    path('', DailyQuestionListView.as_view(), name='daily-questions-list'),
    # path('attempt/', DailyQuestionAttemptView.as_view(), name='daily-question-attempt'),
]

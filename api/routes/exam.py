# api/routes/exam/urls.py
from django.urls import path
from ..views.examViews import ExamListView, ExamDetailView

urlpatterns = [
    path('', ExamListView.as_view(), name='exam-list'),
    path('<int:id>/', ExamDetailView.as_view(), name='exam-detail'),
]

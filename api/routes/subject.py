from django.urls import path
from ..views.subjectViews import *

urlpatterns = [
    path('', SubjectListView.as_view(), name='subject-list'),
    path('<int:id>/', SubjectDetailView.as_view(), name='subject-detail'),
    path('<int:subject_id>/years/', YearsBySubjectView.as_view(), name='filtered-years'),
    path('<int:subject_id>/year/<int:year_id>/topics/', TopicsBySubjectAndYearView.as_view(), name='filtered-topics'),
]

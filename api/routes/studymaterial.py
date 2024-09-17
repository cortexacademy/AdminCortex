from django.urls import path
from ..views.studymaterialViews import StudyMaterialDetailView, StudyMaterialListView

urlpatterns = [
    path("", StudyMaterialListView.as_view(), name="studymaterial-list"),
    path("<int:id>/", StudyMaterialDetailView.as_view(), name="studymaterial-detail"),
]

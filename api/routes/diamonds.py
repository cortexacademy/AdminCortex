from django.urls import path
from ..views.diamondsViews import DiamondDetailView, DiamondListView

urlpatterns = [
    path("", DiamondListView.as_view(), name="diamonds-list"),
    path("<int:id>/", DiamondDetailView.as_view(), name="diamonds-detail"),
]

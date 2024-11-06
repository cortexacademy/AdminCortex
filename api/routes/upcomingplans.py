from django.urls import path
from ..views.upcomingPlans import (
    UpcomingPlanListCreateView,
    UpcomingPlanDetailView,
)

urlpatterns = [
    path(
        "",
        UpcomingPlanListCreateView.as_view(),
        name="upcoming-plan-list-create",
    ),
    path(
        "<int:pk>/",
        UpcomingPlanDetailView.as_view(),
        name="upcoming-plan-detail",
    ),
]

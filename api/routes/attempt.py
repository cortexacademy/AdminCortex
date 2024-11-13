from django.urls import path
from ..views.attemptViews import CreateAttemptView

urlpatterns = [
    path("", CreateAttemptView.as_view(), name="create-attempt"),
]

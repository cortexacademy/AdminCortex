from rest_framework import generics, filters

from api.mixins import AuthMixin, CustomResponseMixin
from api.models import Attempt, Question
from api.serializers import AnalyticsSerializer


class AnalyticsView(AuthMixin, CustomResponseMixin, generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = AnalyticsSerializer
    success_message = "Exams retrieved successfully"

# views.py
from rest_framework import generics
from ..models import UpcomingPlan
from ..serializers import UpcomingPlanSerializer


class UpcomingPlanListCreateView(generics.ListCreateAPIView):
    queryset = UpcomingPlan.objects.all()
    serializer_class = UpcomingPlanSerializer


class UpcomingPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UpcomingPlan.objects.all()
    serializer_class = UpcomingPlanSerializer

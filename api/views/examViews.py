from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.pagination import LimitOffsetPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..models import Exam
from ..serializers import ExamSerializer
from ..mixins import CustomResponseMixin
from django.core.cache import cache

CACHE_TTL = 60 * 60 * 24

@method_decorator(cache_page(CACHE_TTL), name='dispatch')
class ExamListView(CustomResponseMixin, generics.ListAPIView):
    queryset = Exam.objects.prefetch_related(
        'subjects'
    )    
    serializer_class = ExamSerializer
    success_message = "Exams retrieved successfully"
    
    def list(self, request, *args, **kwargs):
        cache.clear()
        response = super().list(request, *args, **kwargs)
        return self.success_response(response.data, message=self.success_message)


@method_decorator(cache_page(CACHE_TTL), name='dispatch')    
class ExamDetailView(CustomResponseMixin, generics.RetrieveAPIView):
    queryset = Exam.objects.prefetch_related(
        'subjects'
    )
    serializer_class = ExamSerializer
    lookup_field = 'id'
    success_message = "Exam retrieved successfully"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(serializer.data, message=self.success_message)

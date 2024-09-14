from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.pagination import LimitOffsetPagination
from ..models import *
from django.db.models import Q
from ..serializers import *
from ..mixins import CustomResponseMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache


CACHE_TTL = 60 * 60 * 24

@method_decorator(cache_page(CACHE_TTL), name='dispatch')
class SubjectListView(CustomResponseMixin, generics.ListAPIView):
    queryset = Subject.objects.prefetch_related('chapter_set')
    serializer_class = SubjectSerializer
    success_message = "Subjects retrieved successfully"
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['name', 'is_active']
    ordering_fields = ['name', 'created_at']
    search_fields = ['name', 'description']

    pagination_class = LimitOffsetPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        created_at = self.request.query_params.get('created_at', None)
        if created_at:
            queryset = queryset.filter(created_at__date=created_at)
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.success_response(response.data, message=self.success_message)


@method_decorator(cache_page(CACHE_TTL), name='dispatch')    
class SubjectDetailView(CustomResponseMixin, generics.RetrieveAPIView):
    queryset = Subject.objects.prefetch_related('chapter_set')
    serializer_class = SubjectSerializer
    lookup_field = 'id'
    success_message = "Subject retrieved successfully"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(serializer.data, message=self.success_message)


@method_decorator(cache_page(CACHE_TTL), name='dispatch')    
class YearsBySubjectView(CustomResponseMixin, generics.ListAPIView):
    serializer_class = YearSerializer
    success_message = "Years retrieved successfully"

    def get_queryset(self):
        subject_id = self.kwargs.get('subject_id')
        years = Year.objects.filter(question__subject__id=subject_id).distinct()
        return years

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.success_response(response.data, message=self.success_message)
  

# @method_decorator(cache_page(CACHE_TTL), name='dispatch')
class TopicsBySubjectAndYearView(CustomResponseMixin, generics.ListAPIView):
    serializer_class = TopicSerializer
    success_message = "Topics retrieved successfully"

    def get_queryset(self):
        # cache.clear()
        subject_id = self.kwargs.get('subject_id')
        year_id = self.kwargs.get('year_id')

        questions = Question.objects.filter(
            Q(subject__id=subject_id) & Q(years__id=year_id)
        )
        topics = Topic.objects.filter(question__in=questions).distinct()
        return topics

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.success_response(response.data, message=self.success_message)
    


from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q

from ..models import *
from ..serializers import *
from ..mixins import CustomResponseMixin
from rest_framework.authentication import SessionAuthentication
from .authViews import CustomTokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated


@authentication_classes([CustomTokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
class QuestionListView(CustomResponseMixin, generics.ListAPIView):
    queryset = Question.objects.all().prefetch_related('years').select_related('solution')
    serializer_class = QuestionSerializer
    success_message = "Questions retrieved successfully"
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['created_at', 'updated_at']
    search_fields = ['statement']
    pagination_class = LimitOffsetPagination
    
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    
    def get_queryset(self):
        queryset = Question.objects.prefetch_related('years').select_related('solution')
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(Q(statement__icontains=search))
        
        created_at = self.request.query_params.get('created_at', None)
        if created_at:
            queryset = queryset.filter(created_at__date=created_at)
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.success_response(response.data, message=self.success_message)



@authentication_classes([CustomTokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
class QuestionDetailView(CustomResponseMixin, generics.RetrieveAPIView):
    queryset = Question.objects.all().prefetch_related('years').select_related('solution')
    serializer_class = QuestionSerializer
    lookup_field = 'id'
    success_message = "Question retrieved successfully"

    def get_serializer_context(self):
        # Pass the request context
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(serializer.data, message=self.success_message)
    
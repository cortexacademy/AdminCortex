from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.pagination import LimitOffsetPagination
from ..mixins import CustomResponseMixin, AuthMixin
from ..models import StudyMaterial
from django.db.models import Q
from ..serializers import StudyMaterialSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache


CACHE_TTL = 60


@method_decorator(cache_page(CACHE_TTL), name="dispatch")
class StudyMaterialListView(AuthMixin, CustomResponseMixin, generics.ListAPIView):
    queryset = StudyMaterial.objects.select_related("subject", "year", "exam")
    serializer_class = StudyMaterialSerializer
    success_message = "Study Materials retrieved successfully"

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = [
        "statement",  # Search within the statement content
        "year__id",  # Search by the year ID
        "subject__id",  # Search by the subject ID
        "exam__id",  # Search by the exam ID
        "year__year",  # Search by the year
        "subject__name",  # Search by the subject name
        "exam__name",  # Search by the exam name
        "is_active",  # Filter by is_active
    ]
    ordering_fields = ["year", "exam", "subject", "created_at"]
    search_fields = [
        "statement",  # Search within the statement content
        "year__id",  # Search by the year ID
        "subject__id",  # Search by the subject ID
        "exam__id",  # Search by the exam ID
        "year__year",  # Search by the year
        "subject__name",  # Search by the subject name
        "exam__name",  # Search by the exam name
    ]

    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        created_at = self.request.query_params.get("created_at", None)
        if created_at:
            queryset = queryset.filter(created_at__date=created_at)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.success_response(response.data, message=self.success_message)


@method_decorator(cache_page(CACHE_TTL), name="dispatch")
class StudyMaterialDetailView(AuthMixin, CustomResponseMixin, generics.RetrieveAPIView):
    queryset = StudyMaterial.objects.select_related("subject", "year", "exam")
    serializer_class = StudyMaterialSerializer
    lookup_field = "id"
    success_message = "Study Material retrieved successfully"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(serializer.data, message=self.success_message)

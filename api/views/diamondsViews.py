from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.pagination import LimitOffsetPagination
from ..mixins import CustomResponseMixin, AuthMixin
from ..models import Diamond
from ..serializers import DiamondSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache


CACHE_TTL = 60


@method_decorator(cache_page(CACHE_TTL), name="dispatch")
class DiamondListView(AuthMixin, CustomResponseMixin, generics.ListAPIView):
    queryset = Diamond.objects.all()
    serializer_class = DiamondSerializer
    success_message = "Diamonds retrieved successfully"

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = [
        "statement",  # Search within the statement content
        "name",  # Search by the exam name
        "is_active",
    ]
    ordering_fields = ["name", "created_at"]
    search_fields = [
        "statement",  # Search within the statement content
        "name",  # Search by the exam name
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
class DiamondDetailView(AuthMixin, CustomResponseMixin, generics.RetrieveAPIView):
    queryset = Diamond.objects.all()
    serializer_class = DiamondSerializer
    lookup_field = "id"
    success_message = "Diamond retrieved successfully"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(serializer.data, message=self.success_message)

from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import date
from ..models import DailyQuestion, Attempt
from ..serializers import DailyQuestionSerializer, DailyQuestionAttemptSerializer
from ..common.authentication import CustomTokenAuthentication
from ..mixins import CustomResponseMixin


@authentication_classes([CustomTokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
class DailyQuestionListView(CustomResponseMixin, generics.ListAPIView):
    serializer_class = DailyQuestionSerializer
    queryset = (
        DailyQuestion.objects.all()
        .select_related("question")
        .prefetch_related(
            # 'question__option_set',
            "question__solution",
            "question__attempt_set",
            "question__years",
        )
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["created_at"]
    search_fields = ["question__statement"]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        date_filter = self.request.query_params.get("date", None)
        if date_filter:
            queryset = queryset.filter(date=date_filter)
        else:
            queryset = queryset.filter(date=date.today())

        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(Q(question__statement__icontains=search))

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page if page is not None else queryset, many=True
        )
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else self.success_response(
                serializer.data, message="Daily questions retrieved successfully"
            )
        )


# @authentication_classes([CustomTokenAuthentication, SessionAuthentication])
# @permission_classes([IsAuthenticated])
# class DailyQuestionAttemptView(CustomResponseMixin, generics.CreateAPIView):
#     serializer_class = DailyQuestionAttemptSerializer

#     def perform_create(self, serializer):
#         user = self.request.user
#         question = serializer.validated_data['question']
#         selected_option = serializer.validated_data['selected_option']

#         attempt, _ = Attempt.objects.update_or_create(
#             user=user,
#             question=question,
#             defaults={'selected_option': selected_option}
#         )
#         return attempt

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         attempt = self.perform_create(serializer)
#         return self.success_response({
#             'attempt': DailyQuestionAttemptSerializer(attempt).data
#         }, message='Question attempted successfully', status=201)

import json
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.mixins import AuthMixin
from ..models import Attempt
from ..serializers import AttemptCreateSerializer, AttemptSerializer
from rest_framework.authentication import SessionAuthentication
from ..common.authentication import (
    CustomTokenAuthentication,
    CustomDjangoModelPermissions,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated

from django.core import serializers


class CreateAttemptView(AuthMixin, generics.CreateAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptCreateSerializer

    def create(self, request, *args, **kwargs):
        attempts_data = request.data.get("attempts", [])
        user = request.user
        created_attempts = []

        for attempt_data in attempts_data:
            question_id = attempt_data.get("question")
            selected_options = attempt_data.get("selected_option", [])

            # Validate that question and selected_options exist
            if not question_id or selected_options is None:
                return Response(
                    {
                        "error": "Each attempt must have a question and selected options."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            attempt = Attempt.objects.filter(
                user=request.user, question__pk=question_id, is_first=True
            ).first()

            if not attempt:
                # # Prepare data for the serializer
                data = {
                    "user": user.id,
                    "question": question_id,
                    "is_first": True,
                }
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                attempt = serializer.save()
                attempt.selected_option.set(selected_options)  # Set many-to-many field
                created_attempts.append(serializer.data)
            else:
                attempt = Attempt.objects.filter(
                    user=request.user, question__pk=question_id, is_first=False
                ).first()

                if not attempt:
                    data = {
                        "user": user.id,
                        "question": question_id,
                        "is_first": False,
                    }
                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    attempt = serializer.save()
                    attempt.selected_option.set(selected_options)
                    created_attempts.append(serializer.data)
                else:
                    serializer = AttemptSerializer(attempt)
                    attempt.selected_option.set(selected_options)
                    created_attempts.append(serializer.data)

        return Response(
            {
                "message": "Attempts created successfully",
                "data": created_attempts,
            },
            status=status.HTTP_201_CREATED,
        )

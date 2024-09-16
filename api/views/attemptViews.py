from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Attempt
from ..serializers import AttemptSerializer
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


@authentication_classes([CustomTokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, CustomDjangoModelPermissions])
class CreateAttemptView(generics.CreateAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Attempt created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

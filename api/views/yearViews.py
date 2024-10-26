from rest_framework import generics
from ..models import Year
from ..serializers import YearSerializer
from ..mixins import CustomResponseMixin


class YearsListView(CustomResponseMixin, generics.ListAPIView):
    queryset = Year.objects.all()
    serializer_class = YearSerializer
    success_message = "Years retrieved successfully"

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.success_response(response.data, message=self.success_message)

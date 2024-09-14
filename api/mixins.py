from rest_framework.response import Response
from rest_framework import status

class CustomResponseMixin:
    success_message = "Operation successful"

    def success_response(self, data, message=None, status_code=status.HTTP_200_OK):
        if not message:
            message = self.success_message
        return Response({
            "status": "success",
            "message": message,
            "data": data
        }, status=status_code)
    
    
    def error_response(self, message="Error", status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "status": "error",
            "message": message,
            "data": None
        }, status=status_code)

from django.http import JsonResponse
from rest_framework.response import Response


def error_json(status="500", message: str = f"Error 500", data: dict = {}):
    return Response({"message": message, "data": data}, status=status)

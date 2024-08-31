from django.http import JsonResponse


def error_json(status = "500", message:str = f"Error 500", data:dict={}):
    return JsonResponse({"message":message,"data":data},status=status)

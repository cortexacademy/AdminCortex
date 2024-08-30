from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def index1(request, id):
    return HttpResponse(f"Hello, world2. You're at the polls index with id {id}.")


def custom_view(request, **kwargs):
    message = kwargs.get('message', 'No message provided.')
    return HttpResponse(f"Message: {message}")
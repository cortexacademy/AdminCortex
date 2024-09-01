import json
from django.http import Http404, HttpResponse
from django.http import JsonResponse
from ..models import Subject
from django.core import serializers
from ..errors import error_json

def index(request):
    # return error_json("405", "Error 404", {"message": "This is a custom error message"})
    subject_list = Subject.objects.all()[:5]
    output = ', '.join([s.name for s in subject_list])
    return HttpResponse(f"Hello, world. \n {output}")

def index1(request, id):
    # subject = serializers.serialize("json", [Subject.objects.get(pk=id)])
    subject = Subject.objects.get(pk=id)
    subject_data = json.loads(serializers.serialize("json", [subject]))[0]  # Get the first item from the list

    return JsonResponse(subject_data, safe=False)
 

def custom_view(request, id):
    subject = Subject.objects.get(pk=id)

    questions = subject.question_set.all()
    questions_data = json.loads(serializers.serialize("json", questions))  # Get the first item from the list

    return JsonResponse(questions_data, safe=False)
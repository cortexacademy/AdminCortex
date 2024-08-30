from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index1/<int:id>/", views.index1, name="index1"),     
    path('custom/', views.custom_view, {'message': 'Hello from kwargs!'}, name='custom_view'),
]
from django.urls import path

from .views import views, authViews

urlpatterns = [
    path("auth/createUser/",authViews.createTempUser,name="createTempUser"),
    path("auth/login/",authViews.login,name="login"),
    path("", views.index, name="index"),
    path("subject/<int:id>/", views.index1, name="index1"),     
    path('subject/<int:id>/questions/', views.custom_view, name="custom_view"),
]   
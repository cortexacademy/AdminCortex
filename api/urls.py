from django.urls import path, include

urlpatterns = [
    path("auth/", include("api.routes.auth")),
    path("subject/", include("api.routes.subject")),
    path("question/", include("api.routes.question")),
    path("dailyquestion/", include("api.routes.dailyquestion")),
    path("exam/", include("api.routes.exam")),
    path("attempt/", include("api.routes.attempt")),
    path("study-material/", include("api.routes.studymaterial")),
    path("diamond/", include("api.routes.diamonds")),
    path("years/", include("api.routes.year")),
    path("upcomingplans/", include("api.routes.upcomingplans")),  # Updated line
    path("upcomingplans/", include("api.routes.upcomingplans")),  # Updated line
    path("analytics/", include("api.routes.analytics")),
]

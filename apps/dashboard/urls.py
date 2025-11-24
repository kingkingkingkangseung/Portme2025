from django.urls import path
from .views import HomeSummaryAPIView, ExperienceNoteView, ExperienceBoardAPIView

urlpatterns = [
    path("summary/", HomeSummaryAPIView.as_view(), name="dashboard-summary"),
    path("notes/", ExperienceNoteView.as_view(), name="dashboard-note"),
    path("experiences/", ExperienceBoardAPIView.as_view(), name="dashboard-experiences"),
]

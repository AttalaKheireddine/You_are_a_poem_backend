
from django.urls import path

from . import views

urlpatterns = [
    path("questions/", views.GetQuestions.as_view()),
    path("get-results/", views.GetResults.as_view()),
]

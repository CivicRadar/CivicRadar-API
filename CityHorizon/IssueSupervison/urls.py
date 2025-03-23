from django.urls import path
from .views import CitizenReportProblem, CitizenReportCitizen

urlpatterns = [
    path('citizen-report-problem/', CitizenReportProblem.as_view()),
    path('citizen-report-citizen/', CitizenReportCitizen.as_view()),
]
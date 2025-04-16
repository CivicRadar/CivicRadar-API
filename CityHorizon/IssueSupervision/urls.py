from django.urls import path
from .views import CitizenReportProblem, CitizenReportCitizen, AllCitizenReport, MayorCityReports, \
                   MayorNotes, MayorDetermineCityProblemSituation

urlpatterns = [
    path('citizen-report-problem/', CitizenReportProblem.as_view()),
    path('citizen-report-citizen/', CitizenReportCitizen.as_view()),
    path('all-citizen-report/', AllCitizenReport.as_view()),
    path('mayor-watch-report/', MayorCityReports.as_view()),
    path('mayor-note/', MayorNotes.as_view()),
    path('mayor-determine-cityproblem-situation/', MayorDetermineCityProblemSituation.as_view()),
]
from django.urls import path
from .views import CitizenReportProblem, CitizenReportCitizen, AllCitizenReport, MayorCityReports, \
                   MayorNotes, MayorDetermineCityProblemSituation, MayorPrioritize, MayorDelegate, MayorDedicatedReportPage, \
                   PublicReport, ReportCount, CityReportCount, CitiesReportCount, ProvincesReportCount, ProvinceReportCount, \
                   ComplexReportCount, HandleCRC

urlpatterns = [
    path('citizen-report-problem/', CitizenReportProblem.as_view()),
    path('citizen-report-citizen/', CitizenReportCitizen.as_view()),
    path('all-citizen-report/', AllCitizenReport.as_view()),
    path('mayor-watch-report/', MayorCityReports.as_view()),
    path('mayor-note/', MayorNotes.as_view()),
    path('mayor-determine-cityproblem-situation/', MayorDetermineCityProblemSituation.as_view()),
    path('mayor-prioritize/', MayorPrioritize.as_view()),
    path('mayor-delegate/', MayorDelegate.as_view()),
    path('mayor-dedicated-report-page/', MayorDedicatedReportPage.as_view()),
    path('public-report/', PublicReport.as_view()),
    path('report-count/', ReportCount.as_view()),
    path('city-report-count/', CityReportCount.as_view()),
    path('cities-report-count/', CitiesReportCount.as_view()),
    path('provinces-report-count/', ProvincesReportCount.as_view()),
    path('province-report-count/', ProvinceReportCount.as_view()),
    path('complex-report-count/', ComplexReportCount.as_view()),
    path('handle-crc/', HandleCRC.as_view()),
]
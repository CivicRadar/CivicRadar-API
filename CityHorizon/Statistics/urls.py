from django.urls import path
from .views import MayorReportView, Counter, LandingCounter

urlpatterns = [
    path('mayor-performance/', MayorReportView.as_view()),
    path('counter/', Counter.as_view()),
    path('landing-counter/', LandingCounter.as_view()),
]
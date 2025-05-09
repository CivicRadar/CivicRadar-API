from django.urls import path
from .views import MayorReportView, Counter

urlpatterns = [
    path('mayor-performance/', MayorReportView.as_view()),
    path('counter/', Counter.as_view()),
]
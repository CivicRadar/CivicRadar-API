from django.urls import path
from .views import MayorReportView

urlpatterns = [
    path('mayor-performance/', MayorReportView.as_view()),
]
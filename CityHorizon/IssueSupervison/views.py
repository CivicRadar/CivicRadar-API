from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
import jwt, datetime

class CitizenReportProblem(APIView):
    def post(self, request):
        # citizen posts a report
        pass

    def get(self, request):
        # citizen gets all his/her reports
        pass

class CitizenReportCitizen(APIView):
    def post(self, request):
        # citizen invalidates other citizen reports
        pass


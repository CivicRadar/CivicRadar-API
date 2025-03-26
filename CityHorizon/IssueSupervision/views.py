from django.contrib.staticfiles.views import serve
from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import CityProblem, ReportCitizen, MayorCities, User, Cities
from .serializers import CityProblemSerializer, ReportCitizenSerializer
import jwt, datetime

class CitizenReportProblem(APIView):
    def post(self, request):
        # citizen posts a report
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        city = Cities.objects.filter(id=request.data['CityID']).first()
        if city is None:
            raise AuthenticationFailed("City not found!")
        problem = CityProblem(City=city, Information=request.data['Information'], Reporter=user, Type=request.data['Type'],
                              Picture=request.data['Picture'], Video=request.data['Video'])
        problem.save()
        serializer = CityProblemSerializer(problem)
        return Response(serializer.data)

    def get(self, request):
        # citizen gets all his/her reports
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        problems = CityProblem.objects.filter(Reporter=user).all()
        serializer = CityProblemSerializer(problems, many=True)
        return Response(serializer.data)

class CitizenReportCitizen(APIView):
    def post(self, request):
        # citizen invalidates other citizen reports
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        problem = CityProblem.objects.filter(id=request.data['CityProblemID']).first()
        if problem is None:
            raise AuthenticationFailed("Problem not found!")
        reportedalready = ReportCitizen.objects.filter(Reported=problem, Reporter=user).first()
        if reportedalready is not None:
            raise AuthenticationFailed("Problem already reported!")
        report = ReportCitizen(Report=request.data['Report'], Reported=problem, Reporter=user)
        report.save()
        serializer = ReportCitizenSerializer(report)
        return Response(serializer.data)

    def get(self, request):
        # citizen gets all his/her reports toward other citizens
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        reports = ReportCitizen.objects.filter(Reporter=user).all()
        serializer = ReportCitizenSerializer(reports, many=True)
        return Response(serializer.data)

class AllCitizenReport(APIView):
    def get(self, request):
        # everybody regradless to their auth token can see all the city problems
        problems = CityProblem.objects.all()
        serializer = CityProblemSerializer(problems, many=True)
        return Response(serializer.data)

class MayorCityReports(APIView):
    def get(self, request):
        # mayor can get the reports in his/her terriority
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cities = MayorCities.objects.filter(User=user).values_list('id', flat=True)
        problems = CityProblem.objects.filter(City__id__in=cities).all()
        serializer = CityProblemSerializer(problems, many=True)
        return Response(serializer.data)
from django.contrib.staticfiles.views import serve
from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import CityProblem, ReportCitizen, MayorCities, User, Cities, MayorNote
from .serializers import CityProblemSerializer, ReportCitizenSerializer, NoteSerializer
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
        cities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
        problems = CityProblem.objects.filter(City__id__in=cities).all()
        serializer = CityProblemSerializer(problems, many=True)
        return Response(serializer.data)

class MayorNotes(APIView):
    def get(self, request):
        # Mayor can see all his/her notes
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

        CityProblemID = request.query_params.get('CityProblemID')
        if not CityProblemID:
            return Response({"error": "CityProblemID is required"}, status=400)

        try:
            cprob = CityProblem.objects.get(id=CityProblemID)
        except CityProblem.DoesNotExist:
            return Response({"error": "City Problem not found!"}, status=404)

        notes = MayorNote.objects.filter(CityProblem=cprob).all()
        serializer = NoteSerializer(notes, many=True, context={'userid': user.id})
        return Response(serializer.data)

    def post(self, request):
        # Mayor can add a note for the report
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

        cityproblem = CityProblem.objects.filter(id=request.data['CityProblemID']).first()
        if cityproblem is None:
            raise AuthenticationFailed("Problem not found!")

        mayorcities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
        if cityproblem.City.id not in mayorcities:
            raise AuthenticationFailed("This Problem does not belong to you!")

        note = MayorNote(NoteOwner=user, Information=request.data['Information'], CityProblem=cityproblem)
        note.save()
        serializer = NoteSerializer(note, context={'userid': user.id})
        return Response(serializer.data)

    def put(self, request):
        # Mayor can update his/her note for the report
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

        note = MayorNote.objects.filter(id=request.data['NoteID'], NoteOwner=user).first()
        if note is None:
            raise AuthenticationFailed("Note not found!")

        note.Information = request.data['Information']
        note.save()
        serializer = NoteSerializer(note, context={'userid': user.id})
        return Response(serializer.data)

    def delete(self, request):
        # Mayor can update his/her note for the report
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

        note = MayorNote.objects.filter(id=request.data['NoteID'], NoteOwner=user).first()
        if note is None:
            raise AuthenticationFailed("Note not found!")

        note.delete()

        return Response({'success': 'note deleted successfully'})
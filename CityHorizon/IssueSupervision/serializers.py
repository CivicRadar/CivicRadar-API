from datetime import timedelta

from django.db.models import Count, Max
from rest_framework import serializers
from Authentication.models import User, Provinces, Cities, CityProblemProsecute, CityProblem, MayorCities, MayorNote
import datetime

class CityProblemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Information = serializers.CharField()
    Type = serializers.CharField()
    Picture = serializers.ImageField()
    Video = serializers.FileField()
    DateTime = serializers.DateTimeField()
    CityID = serializers.IntegerField(source='City.id')
    CityName = serializers.CharField(source='City.Name')
    ProvinceName = serializers.CharField(source='City.Province.Name')
    ReporterID = serializers.IntegerField(source='Reporter.id')
    ReporterName = serializers.CharField(source='Reporter.FullName')
    Longitude = serializers.FloatField()
    Latitude = serializers.FloatField()
    FullAdress = serializers.CharField()
    Status = serializers.CharField()

class ReportCitizenSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    CityName = serializers.CharField(source='Reported.City.Name')
    ProvinceName = serializers.CharField(source='Reported.City.Province.Name')
    Information = serializers.CharField(source='Reported.Information')
    Type = serializers.CharField(source='Reported.Type')
    Picture = serializers.ImageField(source='Reported.Picture')
    Video = serializers.FileField(source='Reported.Video')
    DateTime = serializers.DateTimeField(source='Reported.DateTime')
    CtizenName = serializers.CharField(source='Reported.Reporter.FullName')
    CitizenPicture = serializers.ImageField(source='Reported.Reporter.Picture')

class NoteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Information = serializers.CharField()
    NoteOwner = serializers.IntegerField(source='NoteOwner.id')
    NoteOwnerName = serializers.CharField(source='NoteOwner.FullName')
    NoteOwnerEmail = serializers.CharField(source='NoteOwner.Email')
    NoteOwnerPicture = serializers.ImageField(source='NoteOwner.Picture')
    CityProblem = serializers.IntegerField(source='CityProblem.id')
    PutDeletePermission = serializers.SerializerMethodField()

    def get_PutDeletePermission(self, obj):
        userid = self.context.get('userid', None)
        if userid:
            if userid == obj.NoteOwner.id:
                return True
            return False
        return None
from datetime import timedelta

from django.db.models import Count, Max
from rest_framework import serializers
from Authentication.models import User, Provinces, Cities, CityProblemProsecute, CityProblem, MayorCities, MayorNote
import datetime

class CityProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityProblem
        fields = '__all__'

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

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MayorNote
        fields = '__all__'
from rest_framework import serializers
from .models import Provinces, Cities, CityZones, MayorZones

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provinces
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = '__all__'

class MayorCityZoneSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    MayorID = serializers.IntegerField(source='User.id')
    MayorFullName = serializers.CharField(source='User.FullName')
    MayorEmail = serializers.EmailField(source='User.Email')
    CityZone = serializers.IntegerField(source='CityZone.Number')
    City = serializers.CharField(source='CityZone.City.Name')
    Province = serializers.CharField(source='CityZone.City.Province.Name')
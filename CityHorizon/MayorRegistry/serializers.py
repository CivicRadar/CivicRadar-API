from rest_framework import serializers
from .models import Provinces, Cities

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provinces
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = '__all__'

class MayorCitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    MayorID = serializers.IntegerField(source='User.id')
    MayorFullName = serializers.CharField(source='User.FullName')
    MayorEmail = serializers.EmailField(source='User.Email')
    City = serializers.CharField(source='City.Name')
    CityID = serializers.CharField(source='City.id')
    Province = serializers.CharField(source='City.Province.Name')

class MayorInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    FullName = serializers.CharField()
    Email = serializers.EmailField()


from datetime import timedelta

from django.db.models import Count, Max
from rest_framework import serializers
from Authentication.models import Provinces, Cities, CityProblem, MayorCities, User, Notification
import datetime

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

class MayorComplexSerializer(serializers.ModelSerializer):
    monthly_report_check = serializers.SerializerMethodField()
    monthly_report_check_percentage = serializers.SerializerMethodField()
    cities = serializers.SerializerMethodField()
    maximum_monthly_report_check = serializers.SerializerMethodField()
    LastCooperation = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'FullName', 'Email', 'LastCooperation', 'monthly_report_check', 'monthly_report_check_percentage', 'maximum_monthly_report_check', 'cities']

    def get_monthly_report_check(self, obj):
        now = datetime.datetime.now()
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        counter = Notification.objects.filter(Sender=obj, Date__gte=current_month).count()
        return counter

    def get_monthly_report_check_percentage(self, obj):
        now = datetime.datetime.now()
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        counter_current = Notification.objects.filter(Sender=obj, Date__gte=current_month).count()
        last_month = (current_month - timedelta(days=1) ).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        counter_last = Notification.objects.filter(Sender=obj, Date__gte=last_month, Date__lte=current_month).count()
        if counter_current>counter_last:
            return int(100 *(counter_current-counter_last)/counter_current)
        elif counter_last == 0:
            return 0
        return int(100 *(counter_current-counter_last) / counter_last)

    def get_cities(self, obj):
        mayorcities = MayorCities.objects.filter(User=obj).values_list('City__id', flat=True)
        cities = Cities.objects.filter(id__in=mayorcities).all()
        serializer = CitySerializer(cities, many=True)
        return serializer.data

    def get_maximum_monthly_report_check(self, obj):
        now = datetime.datetime.now()
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        maximum = Notification.objects.filter(Date__gte=current_month, Sender=obj).values('Sender__id').annotate(cooperation_count=Count('Sender__id')).aggregate(max_cooperation=Max('cooperation_count'))
        return maximum['max_cooperation']

    def get_LastCooperation(self, obj):
        notif = Notification.objects.filter(Sender=obj).order_by('Date').first()
        if notif is None:
            return None
        return notif.Date
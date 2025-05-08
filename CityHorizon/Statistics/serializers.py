from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.db.models import Max
from .models import MayorReport
from IssueSupervision.serializers import OrganizationSerializer
from MayorRegistry.serializers import CitySerializer, ProvinceSerializer
from Authentication.models import Organization, MayorCities, CityProblem, Notification

class MayorReportSerializer(serializers.ModelSerializer):
    Organizations = SerializerMethodField()
    Mayor_Name = SerializerMethodField()
    Mayor_Email = SerializerMethodField()
    Mayor_Cities = SerializerMethodField()
    Mayor_Provinces = SerializerMethodField()
    Mayor_CityProblems = SerializerMethodField()
    Mayor_LastCooperation = SerializerMethodField()

    class Meta:
        model = MayorReport
        fields = ['report_date', 'problem_status_pie_chart', 'problem_type_bar_chart', 'engagement_bar_chart',
                  'resolved_over_time_line_chart', 'transition_time_bar_chart', 'Organizations', 'Mayor_Name',
                  'Mayor_Email', 'Mayor_Cities', 'Mayor_Provinces', 'Mayor_CityProblems', 'Mayor_LastCooperation']

    def get_Organizations(self, obj):
        organs = Organization.objects.filter(Owner=obj.Mayor).all()
        return OrganizationSerializer(organs, many=True).data

    def get_Mayor_Name(self, obj):
        return obj.Mayor.FullName

    def get_Mayor_Email(self, obj):
        return obj.Mayor.Email

    def get_Mayor_Cities(self, obj):
        return MayorCities.objects.filter(User=obj.Mayor).values_list('City__Name', flat=True)

    def get_Mayor_Provinces(self, obj):
        return MayorCities.objects.filter(User=obj.Mayor).values_list('City__Province__Name', flat=True)

    def get_Mayor_CityProblems(self, obj):
        cities = MayorCities.objects.filter(User=obj.Mayor).values_list('City__id', flat=True)
        return CityProblem.objects.filter(City__id__in=cities).count()

    def get_Mayor_LastCooperation(self, obj):
        # Find the latest notification date for the sender
        latest_notification = Notification.objects.filter(Sender=obj.Mayor).aggregate(last_date=Max('Date'))
        # Return the last date if it exists, otherwise None
        return latest_notification['last_date']
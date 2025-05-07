from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import MayorReport
from IssueSupervision.serializers import OrganizationSerializer
from MayorRegistry.serializers import CitySerializer, ProvinceSerializer
from Authentication.models import Organization, MayorCities

class MayorReportSerializer(serializers.ModelSerializer):
    Organizations = SerializerMethodField()
    Mayor_Name = SerializerMethodField()
    Mayor_Email = SerializerMethodField()
    Mayor_Cities = SerializerMethodField()
    Mayor_Provinces = SerializerMethodField()

    class Meta:
        model = MayorReport
        fields = ['report_date', 'problem_status_pie_chart', 'problem_type_bar_chart', 'engagement_bar_chart',
                  'resolved_over_time_line_chart', 'transition_time_bar_chart', 'Organizations', 'Mayor_Name',
                  'Mayor_Email', 'Mayor_Cities', 'Mayor_Provinces']

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
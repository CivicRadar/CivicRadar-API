from django.db.models import Avg, F, FloatField
from django.db.models.expressions import ExpressionWrapper
import datetime
from datetime import timedelta
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.db.models import Max
from IssueSupervision.serializers import OrganizationSerializer
from MayorRegistry.serializers import CitySerializer, ProvinceSerializer
from Authentication.models import Organization, MayorCities, CityProblem, Notification, User, CityProblemReaction

class MayorReportSerializer(serializers.ModelSerializer):
    Organizations = SerializerMethodField()
    Mayor_Name = SerializerMethodField()
    Mayor_Email = SerializerMethodField()
    Mayor_Cities = SerializerMethodField()
    Mayor_Provinces = SerializerMethodField()
    Mayor_CityProblems = SerializerMethodField()
    Mayor_LastCooperation = SerializerMethodField()
    problem_type_bar_chart = SerializerMethodField()
    problem_status_pie_chart = SerializerMethodField()
    engagement_bar_chart = SerializerMethodField()
    resolved_over_time_line_chart = SerializerMethodField()
    transition_time_bar_chart = SerializerMethodField()

    class Meta:
        model = User
        fields = ['problem_status_pie_chart', 'problem_type_bar_chart', 'engagement_bar_chart',
                  'resolved_over_time_line_chart', 'transition_time_bar_chart', 'Organizations', 'Mayor_Name',
                  'Mayor_Email', 'Mayor_Cities', 'Mayor_Provinces', 'Mayor_CityProblems', 'Mayor_LastCooperation']

    def get_Organizations(self, obj):
        organs = Organization.objects.filter(Owner=obj).all()
        return OrganizationSerializer(organs, many=True).data

    def get_Mayor_Name(self, obj):
        return obj.FullName

    def get_Mayor_Email(self, obj):
        return obj.Email

    def get_Mayor_Cities(self, obj):
        return MayorCities.objects.filter(User=obj).values_list('City__Name', flat=True)

    def get_Mayor_Provinces(self, obj):
        return MayorCities.objects.filter(User=obj).values_list('City__Province__Name', flat=True)

    def get_Mayor_CityProblems(self, obj):
        cities = MayorCities.objects.filter(User=obj).values_list('City__id', flat=True)
        return CityProblem.objects.filter(City__id__in=cities).count()

    def get_Mayor_LastCooperation(self, obj):
        # Find the latest notification date for the sender
        latest_notification = Notification.objects.filter(Sender=obj).aggregate(last_date=Max('Date'))
        # Return the last date if it exists, otherwise None
        return latest_notification['last_date']

    def get_problem_type_bar_chart(self, obj):
        mydict = dict()
        cities = MayorCities.objects.filter(User=obj).values_list('City__id', flat=True)
        lnum = CityProblem.objects.filter(City__id__in=cities, Type='Lighting').count()
        gnum = CityProblem.objects.filter(City__id__in=cities, Type='Garbage').count()
        snum = CityProblem.objects.filter(City__id__in=cities, Type='Street').count()
        onum = CityProblem.objects.filter(City__id__in=cities, Type='Other').count()
        mydict.update({"Lighting": lnum, "Garbage": gnum, "Street": snum, "Other": onum})
        return mydict

    def get_problem_status_pie_chart(self, obj):
        mydict = dict()
        cities = MayorCities.objects.filter(User=obj).values_list('City__id', flat=True)
        cnt = CityProblem.objects.filter(City__id__in=cities).count()
        if cnt > 0:
            prnum = CityProblem.objects.filter(City__id__in=cities, Status='PendingReview').count()
            irnum = Notification.objects.filter(Sender=obj, UpdatedTo='IssueResolved').count()
            irnum_id = Notification.objects.filter(UpdatedTo='IssueResolved').values_list('CityProblem__id', flat=True)
            ucnum = Notification.objects.filter(Sender=obj, UpdatedTo='UnderConsideration').exclude(CityProblem__id__in=irnum_id).count()
            if prnum+irnum+ucnum == 0:
                mydict.update({'PendingReview': 0, 'UnderConsideration': 0, 'IssueResolved': 100})
                return mydict
            total = prnum + irnum + ucnum
            n2 = (100*ucnum) // total
            n3 = (100*irnum) // total
            n1 = 100-n2-n3
            mydict.update({'PendingReview': n1, 'UnderConsideration': n2, 'IssueResolved': n3})
            return mydict
        mydict.update({'PendingReview':0, 'UnderConsideration':0, 'IssueResolved':100})
        return mydict

    def get_engagement_bar_chart(self, obj):
        mydict = dict()
        cities = MayorCities.objects.filter(User=obj).values_list('City__id', flat=True)
        liks = CityProblemReaction.objects.filter(CityProblem__City__id__in=cities, Like=True).count()
        diss = CityProblemReaction.objects.filter(CityProblem__City__id__in=cities, Like=False).count()
        mydict.update({"Likes":liks, "Dislikes":diss})
        return mydict

    def get_resolved_over_time_line_chart(self, obj):
        mydict = dict()
        now = datetime.datetime.now()
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        counter_current = Notification.objects.filter(Sender=obj, Date__gte=current_month, UpdatedTo='IssueResolved').count()
        mydict.update({current_month.strftime("%B %Y"): counter_current})
        for i in range(5):
            last_month = (current_month - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            counter_last = Notification.objects.filter(Sender=obj, Date__gte=last_month, Date__lt=current_month, UpdatedTo='IssueResolved').count()
            mydict.update({last_month.strftime("%B %Y"): counter_last})
            current_month=last_month
        return mydict

    def get_transition_time_bar_chart(self, obj):
        mydict = dict()

        # Helper function to calculate average days for a given type and status
        def calculate_avg_days(notification_type, updated_to, obj):
            queryset = (
                Notification.objects.filter(
                    Sender=obj,
                    UpdatedTo=updated_to,
                    CityProblem__City__in=MayorCities.objects.filter(User=obj).values('City'),
                    CityProblem__Type=notification_type
                )
                .annotate(
                    time_diff=(F('Date') - F('CityProblem__DateTime'))
                )
                .values('time_diff')
            )

            # Fetch all time_diff values and calculate average in Python
            time_diffs = [item['time_diff'].total_seconds() / 86400.0 for item in queryset if
                          item['time_diff'] is not None]
            return sum(time_diffs) / len(time_diffs) if time_diffs else 0

        # Calculate averages for Lighting
        mydict.update({
            "Lighting_UnderConsideration": calculate_avg_days('Lighting', 'UnderConsideration', obj),
            "Lighting_IssueResolved": calculate_avg_days('Lighting', 'IssueResolved', obj)
        })

        # Calculate averages for Garbage
        mydict.update({
            "Garbage_UnderConsideration": calculate_avg_days('Garbage', 'UnderConsideration', obj),
            "Garbage_IssueResolved": calculate_avg_days('Garbage', 'IssueResolved', obj)
        })

        # Calculate averages for Other
        mydict.update({
            "Other_UnderConsideration": calculate_avg_days('Other', 'UnderConsideration', obj),
            "Other_IssueResolved": calculate_avg_days('Other', 'IssueResolved', obj)
        })

        # Calculate averages for Street
        mydict.update({
            "Street_UnderConsideration": calculate_avg_days('Street', 'UnderConsideration', obj),
            "Street_IssueResolved": calculate_avg_days('Street', 'IssueResolved', obj)
        })

        return mydict
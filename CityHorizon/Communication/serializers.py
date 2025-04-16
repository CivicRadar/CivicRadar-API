from rest_framework import serializers
from Authentication.models import User, Notification
import datetime


class NotoficationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Message = serializers.CharField()
    CityProblemID = serializers.IntegerField(source='CityProblem.id')
    Date = serializers.DateTimeField()
    Seen = serializers.BooleanField()
    SenderID = serializers.CharField(source='Sender.id')
    SenderFullName = serializers.CharField(source='Sender.FullName')
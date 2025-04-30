from datetime import timedelta
from django.db.models import Count, Max
from rest_framework import serializers
from Authentication.models import (User, Provinces, Cities, CityProblemProsecute, CityProblem, MayorCities,
                                   MayorNote, CityProblemReaction, MayorPriority, Notification)


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
    ReporterPicture = serializers.ImageField(source='Reporter.Picture')
    Longitude = serializers.FloatField()
    Latitude = serializers.FloatField()
    FullAdress = serializers.CharField()
    Status = serializers.CharField()
    Likes = serializers.SerializerMethodField()
    Dislikes = serializers.SerializerMethodField()
    YourReaction = serializers.SerializerMethodField()

    def get_Likes(self, obj):
        return CityProblemReaction.objects.filter(CityProblem=obj, Like=True).count()

    def get_Dislikes(self, obj):
        return CityProblemReaction.objects.filter(CityProblem=obj, Like=False).count()

    def get_YourReaction(self, obj):
        if 'userID' in self.context:
            myobject = CityProblemReaction.objects.filter(CityProblem=obj, Reactor__id=self.context['userID']).first()
            if myobject is None:
                return None
            return myobject.Like
        return None

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

class MayorPrioritySerializer(serializers.Serializer):
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
    ReporterPicture = serializers.ImageField(source='Reporter.Picture')
    Longitude = serializers.FloatField()
    Latitude = serializers.FloatField()
    FullAdress = serializers.CharField()
    Status = serializers.CharField()
    Likes = serializers.SerializerMethodField()
    Dislikes = serializers.SerializerMethodField()
    YourReaction = serializers.SerializerMethodField()
    Priority = serializers.SerializerMethodField()

    def get_Likes(self, obj):
        return CityProblemReaction.objects.filter(CityProblem=obj, Like=True).count()

    def get_Dislikes(self, obj):
        return CityProblemReaction.objects.filter(CityProblem=obj, Like=False).count()

    def get_YourReaction(self, obj):
        if 'userID' in self.context:
            myobject = CityProblemReaction.objects.filter(CityProblem=obj, Reactor__id=self.context['userID']).first()
            if myobject is None:
                return None
            return myobject.Like
        return None

    def get_Priority(self, obj):
        prio = MayorPriority.objects.filter(Mayor__id=self.context['userID'], CityProblem=obj).first()
        if prio is None:
            return None
        return prio.Priority

class NotifMayorSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='Sender.id')
    FulllName = serializers.CharField(source='Sender.FullName')
    Email = serializers.CharField(source='Sender.Email')
    Picture = serializers.ImageField(source='Sender.Picture')
    Date = serializers.DateTimeField()

class MayorCompleteCityProblemSerializer(serializers.Serializer):
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
    ReporterEmail = serializers.CharField(source='Reporter.Email')
    ReporterPicture = serializers.ImageField(source='Reporter.Picture')
    Longitude = serializers.FloatField()
    Latitude = serializers.FloatField()
    FullAdress = serializers.CharField()
    Status = serializers.CharField()
    Likes = serializers.SerializerMethodField()
    Dislikes = serializers.SerializerMethodField()
    YourReaction = serializers.SerializerMethodField()
    Priority = serializers.SerializerMethodField()
    Verified = serializers.SerializerMethodField()
    VerificationDate = serializers.SerializerMethodField()
    ConsideredByMayor = serializers.SerializerMethodField()
    ResolvedByMayor = serializers.SerializerMethodField()

    def get_Likes(self, obj):
        return CityProblemReaction.objects.filter(CityProblem=obj, Like=True).count()

    def get_Dislikes(self, obj):
        return CityProblemReaction.objects.filter(CityProblem=obj, Like=False).count()

    def get_YourReaction(self, obj):
        if 'userID' in self.context:
            myobject = CityProblemReaction.objects.filter(CityProblem=obj, Reactor__id=self.context['userID']).first()
            if myobject is None:
                return None
            return myobject.Like
        return None

    def get_Priority(self, obj):
        prio = MayorPriority.objects.filter(Mayor__id=self.context['userID'], CityProblem=obj).first()
        if prio is None:
            return None
        return prio.Priority

    def get_Verified(self, obj):
        return True

    def get_VerificationDate(self, obj):
        return obj.DateTime

    def get_ConsideredByMayor(self, obj):
        conotif = Notification.objects.filter(Sender__id=self.context['userID'], UpdatedTo='UnderConsideration',
                                              CityProblem=obj).first()
        if conotif is None:
            resnotif = Notification.objects.filter(Sender__id=self.context['userID'], UpdatedTo='IssueResolved',
                                                   CityProblem=obj).first()
            if resnotif is None:
                return None
            return NotifMayorSerializer(resnotif).data
        return NotifMayorSerializer(conotif).data

    def get_ResolvedByMayor(self, obj):
        resnotif = Notification.objects.filter(Sender__id=self.context['userID'], UpdatedTo='IssueResolved',
                                               CityProblem=obj).first()
        if resnotif is None:
            return None
        return NotifMayorSerializer(resnotif).data

class OrganizationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Type = serializers.CharField()
    OrganHead_FullName = serializers.CharField()
    OrganHead_Email = serializers.EmailField()
    OrganHead_Number = serializers.CharField()
    CityName = serializers.CharField(source='City.Name')
    ProvinceName = serializers.CharField(source='City.Province.Name')

class CityProblemCountSerializer(serializers.ModelSerializer):
    problems_count = serializers.IntegerField()

    class Meta:
        model = Cities
        fields = ['id', 'Name', 'problems_count']

class ProvinceProblemCountSerializer(serializers.ModelSerializer):
    problems_count = serializers.IntegerField()

    class Meta:
        model = Provinces
        fields = ['id', 'Name', 'problems_count']


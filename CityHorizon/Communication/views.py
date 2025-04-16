from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import CityProblem, ReportCitizen, MayorCities, User, Cities, MayorNote, Notification
from .serializers import NotoficationSerializer
import jwt, datetime


# Create your views here.
class Notifications(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        notifs = Notification.objects.filter(Receiver=user).all()
        serializer = NotoficationSerializer(notifs, many=True)
        return Response(serializer.data)
    def put(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        notif = Notification.objects.filter(Receiver=user, id=request.data['NotificationID']).first()
        if notif is None:
            raise AuthenticationFailed("Notification not found!")
        if notif.Seen:
            return Response({"success":"you have already seen this massage"})
        notif.Seen=True
        notif.save()
        return Response({"success":"you have seen this message"})
from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import User, Notification, CityProblemReaction, CityProblem
from .serializers import NotoficationSerializer, CityProblemReactionSerializer, PointsSerializer
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

class Like(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cityproblem = CityProblem.objects.filter(id=request.data['CityProblemID']).first()
        if cityproblem is None:
            raise AuthenticationFailed("City problem not found!")
        react = CityProblemReaction.objects.filter(Reactor=user, CityProblem=cityproblem).first()
        if react is None:
            newreact = CityProblemReaction(Reactor=user, CityProblem=cityproblem, Like=request.data['Like'])
            newreact.save()
            serializer = CityProblemReactionSerializer(newreact)
            return Response(serializer.data)
        elif react.Like == request.data['Like']:
            react.delete()
            return Response({"Like":None})
        else:
            react.Like = request.data['Like']
            react.save()
            serializer = CityProblemReactionSerializer(react)
            return Response(serializer.data)

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cityproblem = CityProblem.objects.filter(id=request.query_params['CityProblemID']).first()
        if cityproblem is None:
            raise AuthenticationFailed("City problem not found!")
        react = CityProblemReaction.objects.filter(Reactor=user, CityProblem=cityproblem).first()
        if react is None:
            return Response({"Like":None})
        return Response({"Like":react.Like})

class Points(APIView):
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
        serializer =  PointsSerializer(user, context={'request':request})
        return Response(serializer.data)
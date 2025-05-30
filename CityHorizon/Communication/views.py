from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import (User, Notification, CityProblemReaction, CityProblem,
                                   Comment, CommentReaction, MayorNotification, MayorCities)
from django.db.models import Count, Q
from .serializers import (NotoficationSerializer, CityProblemReactionSerializer, PointsSerializer,
                          CommentSerializer, CommentReactionSerializer, MayorNotoficationSerializer)
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

        if user.NotificationDeactivationTime is None:
            notifs = Notification.objects.filter(Receiver=user).all()
            serializer = NotoficationSerializer(notifs, many=True)
            return Response(serializer.data)
        else:
            notifs = Notification.objects.filter(Receiver=user, Date__lt=user.NotificationDeactivationTime).all()
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

class MayorNotifications(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        current = datetime.datetime.now().date()
        notif = MayorNotification.objects.filter(Receiver=user, OnlyDate=current).first()
        if notif is None:
            mayor_cities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
            most_liked_problem = CityProblem.objects.filter(
                City__id__in=mayor_cities
            ).annotate(
                like_count=Count('cityproblemreaction', filter=Q(cityproblemreaction__Like=True))
            ).order_by('-like_count').first()
            if most_liked_problem is not None:
                # Create a MayorNotification
                mymessage = f"جناب شهردار، یک مشکل مهم در شهر {most_liked_problem.City.Name} گزارش شده است. لطفا این موضوع را جهت بررسی و اقدام لازم در اولویت قرار دهید."
                myobj = MayorNotification.objects.create(
                    Message=mymessage,
                    Receiver=user,
                    CityProblem=most_liked_problem,
                    Sender=most_liked_problem.Reporter,  # Assuming the reporter is the sender
                    Seen=False
                )
                myobj.full_clean()
                myobj.save()

        if user.NotificationDeactivationTime is None:
            notifs = MayorNotification.objects.filter(Receiver=user).all()
            serializer = MayorNotoficationSerializer(notifs, many=True)
            return Response(serializer.data)
        else:
            notifs = Notification.objects.filter(Receiver=user, Date__lt=user.NotificationDeactivationTime).all()
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

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        notif = MayorNotification.objects.filter(Receiver=user, id=request.data['NotificationID']).first()
        if notif is None:
            raise AuthenticationFailed("Notification not found!")
        if notif.Seen:
            return Response({"success": "you have already seen this massage"})
        notif.Seen = True
        notif.save()
        return Response({"success": "you have seen this message"})

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

class Comments(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            myvar = request.query_params.get('CityProblemID')
            if myvar is None:
                raise AuthenticationFailed("variable name is wrong or value is null")
            cprobe = CityProblem.objects.filter(id=myvar).first()
            if cprobe is None:
                raise AuthenticationFailed("City problem not found!")
            comments = Comment.objects.filter(CityProblem=cprobe, IsAReply=False).all()
            serialzier = CommentSerializer(comments, many=True)
            return Response(serialzier.data)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        myvar = request.query_params.get('CityProblemID')
        if myvar is None:
            raise AuthenticationFailed("variable name is wrong or value is null")
        cprobe = CityProblem.objects.filter(id=myvar).first()
        if cprobe is None:
            raise AuthenticationFailed("City problem not found!")
        comments = Comment.objects.filter(CityProblem=cprobe, IsAReply=False).all()
        serialzier = CommentSerializer(comments, many=True, context={'userid':user.id})
        return Response(serialzier.data)

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
        cprobe = CityProblem.objects.filter(id=request.data['CityProblemID']).first()
        if cprobe is None:
            raise AuthenticationFailed("City problem not found!")
        isanony = False
        if "IsAnonymous" in request.data:
            isanony = request.data['IsAnonymous']
        comment = Comment(Sender=user, Content=request.data['Content'],
                          CityProblem=cprobe,
                          IsAReply=request.data['IsAReply'],
                          ReplyID=request.data['ReplyID'],
                          IsAnonymous=isanony)
        comment.full_clean()
        comment.save()
        return Response({"Success":"You posted a message!"})

class CommentReactions(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            return Response({"Like": None})

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({"Like": None})

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            return Response({"Like": None})

        comment = Comment.objects.filter(id=request.query_params['CommentID']).first()
        if comment is None:
            return Response({"Like": None})

        react = CommentReaction.objects.filter(Reactor=user, Comment=comment).first()
        if react is None:
            return Response({"Like": None})

        return Response({"Like": react.Like})

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

        comment = Comment.objects.filter(id=request.data['CommentID']).first()
        if comment is None:
            raise AuthenticationFailed("Comment not found!")
        react = CommentReaction.objects.filter(Reactor=user, Comment=comment).first()
        if react is None:
            newreact = CommentReaction(Reactor=user, Comment=comment, Like=request.data['Like'])
            newreact.save()
            serializer = CommentReactionSerializer(newreact)
            return Response(serializer.data)
        elif react.Like == request.data['Like']:
            react.delete()
            return Response({"Like":None})
        else:
            react.Like = request.data['Like']
            react.save()
            serializer = CommentReactionSerializer(react)
            return Response(serializer.data)

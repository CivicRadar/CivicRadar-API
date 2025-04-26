from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import User, Notification, CityProblemReaction, CityProblem, Comment, CommentReaction
from .serializers import NotoficationSerializer, CityProblemReactionSerializer, PointsSerializer, CommentSerializer, CommentReactionSerializer
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

class Comments(APIView):
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
        if user.Type == 'Admin':
            raise AuthenticationFailed("You can't comment as an admin!")
        myvar = request.query_params.get('CityProblemID')
        if myvar is None:
            raise AuthenticationFailed("variable name is wrong or value is null")
        cprobe = CityProblem.objects.filter(id=myvar).first()
        if cprobe is None:
            raise AuthenticationFailed("City problem not found!")
        comments = Comment.objects.filter(CityProblem=cprobe).all()
        serialzier = CommentSerializer(comments, many=True)
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
        if user.Type == 'Admin':
            raise AuthenticationFailed("You can't comment as an admin!")
        cprobe = CityProblem.objects.filter(id=request.data['CityProblemID']).first()
        if cprobe is None:
            raise AuthenticationFailed("City problem not found!")
        comment = Comment(Sender=user, Content=request.data['Content'],
                          CityProblem=cprobe,
                          IsAReply=request.data['IsAReply'],
                          ReplyID=request.data['ReplyID'])
        comment.full_clean()
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

class CommentReactions(APIView):
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
        if user.Type == 'Admin':
            raise AuthenticationFailed("You can't comment as an admin!")

        comment = Comment.objects.filter(id=request.query_params['CommentID']).first()
        if comment is None:
            raise AuthenticationFailed("City problem not found!")
        react = CommentReaction.objects.filter(Reactor=user, Comment=comment).first()
        if react is None:
            return Response({"Like":None})
        return Response({"Like":react.Like})

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
        if user.Type == 'Admin':
            raise AuthenticationFailed("You can't comment as an admin!")

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

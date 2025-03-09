from django.conf import settings
from django.shortcuts import render
from decouple import config
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User
import jwt, datetime


class SignUp(APIView):
    def post(self, request):
        request.data['Type']='Citizen'
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class Login(APIView):
    def post(self, request):
        email = request.data['Email']
        password = request.data['Password']
        typeof = request.data['Type']

        user = User.objects.filter(Email=email, Type=typeof).first()

        if user is not None and user.check_password(password):

            payload = {
                'id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
                'iat': datetime.datetime.utcnow()
            }

            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            response = Response()
            response.set_cookie(key='jwt', value=token, httponly=True, secure=config('COOKIE_SECURE', cast=bool))
            response.data = {'jwt': token}
            return response
        return Response({'fail': 'your email or password is incorrect'})

class Profile(APIView):
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

        serializer = UserSerializer(user)
        return Response(serializer.data)
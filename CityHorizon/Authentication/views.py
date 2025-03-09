from django.conf import settings
from django.shortcuts import render
from decouple import config
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User
import jwt, datetime


class SignUp(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class Login(APIView):
    def post(self, request):
        email = request.data['Email']
        password = request.data['Password']

        user = User.objects.filter(Email=email).first()

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
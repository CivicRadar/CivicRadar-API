from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import User
from .models import Provinces, Cities, CityZones, MayorZones
from Authentication.serializers import UserSerializer, UserIDSerializer
from .serializers import ProvinceSerializer, CitySerializer, MayorCityZoneSerializer
import jwt, datetime

# Create your views here.
class Add(APIView):
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
        serializer = UserSerializer(user)
        if serializer.data['Type']!= 'Admin':
            raise AuthenticationFailed("You are Not Admin!")
        request.data['Type']='Mayor'
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class List(APIView):
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
        if serializer.data['Type']!= 'Admin':
            raise AuthenticationFailed("You are Not Admin!")
        users = User.objects.filter(Type='Mayor').all()
        serializer = UserIDSerializer(users, many=True)
        return Response(serializer.data)

class Update(APIView):
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
        serializer = UserSerializer(user)
        if serializer.data['Type']!= 'Admin':
            raise AuthenticationFailed("You are Not Admin!")
        mayor = User.objects.filter(id=request.data['id'], Type='Mayor').first()
        if mayor is None:
            raise AuthenticationFailed("Mayor not found!")
        mayor.Email = request.data['Email']
        mayor.FullName = request.data['FullName']
        mayor.set_password(request.data['Password'])
        mayor.save()
        serializer2 = UserSerializer(mayor)
        return Response(serializer2.data)

class Delete(APIView):
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
        serializer = UserSerializer(user)
        if serializer.data['Type']!= 'Admin':
            raise AuthenticationFailed("You are Not Admin!")

        mayor = User.objects.filter(id=request.data['id'], Type='Mayor').first()
        if mayor is None:
            raise AuthenticationFailed("Mayor not found!")
        mayor.delete()
        return Response({'success': 'Deleted successfully!'})

class ProvinceList(APIView):
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
        if serializer.data['Type']!= 'Admin':
            raise AuthenticationFailed("You are Not Admin!")

        myprovinces = Provinces.objects.all()
        serializer = ProvinceSerializer(myprovinces, many=True)
        return Response(serializer.data)

class CityList(APIView):
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
        serializer = UserSerializer(user)
        if serializer.data['Type']!= 'Admin':
            raise AuthenticationFailed("You are Not Admin!")

        myprovince = Provinces.objects.filter(id=request.data['ProvinceID']).first()
        if myprovince is None:
            return Response({'fail': 'Province not found!'})

        mycities = Cities.objects.filter(Province=myprovince).all()
        serializer = CitySerializer(mycities, many=True)
        return Response(serializer.data)

class AddMayorZone(APIView):
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
        serializer = UserSerializer(user)
        if serializer.data['Type']!= 'Admin':
            raise AuthenticationFailed("You are Not Admin!")

        city = Cities.objects.filter(id=request.data['CityID']).first()
        if city is None:
            raise AuthenticationFailed("City not found!")
        cityzone = CityZones.objects.filter(Number=request.data['CityZoneNumber']).first()
        if cityzone is None:
            cityzone = CityZones.objects.create(Number=request.data['CityZoneNumber'], City=city)

        mayor = User.objects.filter(id=request.data['MayorID'], Type='Mayor').first()
        if mayor is None:
            raise AuthenticationFailed("Mayor not found!")
        mayorzone = MayorZones.objects.filter(User=mayor, CityZone=cityzone).first()
        if mayorzone is None:
            mayorzone = MayorZones(User=mayor, CityZone=cityzone)
            mayorzone.save()
            return Response({'success': 'Mayor zone added!'})
        return Response({'fail': 'Mayor already added!'})

class ListMayorZone(APIView):
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
        serializer = UserSerializer(user)
        if serializer.data['Type']!= 'Admin':
            raise AuthenticationFailed("You are Not Admin!")

        mayor = User.objects.filter(id=request.data['MayorID'], Type='Mayor').first()
        if mayor is None:
            raise AuthenticationFailed("Mayor not found!")

        mayorzones = MayorZones.objects.filter(User=mayor).all()
        serializer = MayorCityZoneSerializer(mayorzones, many=True)
        return Response(serializer.data)

class RemoveMayorZone(APIView):
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
        serializer = UserSerializer(user)
        if serializer.data['Type']!= 'Admin':
            raise AuthenticationFailed("You are Not Admin!")

        city = Cities.objects.filter(id=request.data['CityID']).first()
        if city is None:
            raise AuthenticationFailed("City not found!")
        cityzone = CityZones.objects.filter(Number=request.data['CityZoneNumber']).first()
        if cityzone is None:
            cityzone = CityZones.objects.create(Number=request.data['CityZoneNumber'], City=city)

        mayor = User.objects.filter(id=request.data['MayorID'], Type='Mayor').first()
        if mayor is None:
            raise AuthenticationFailed("Mayor not found!")
        mayorzone = MayorZones.objects.filter(User=mayor, CityZone=cityzone).first()
        if mayorzone is None:
            return Response({'fail': 'Mayor zone does not exist'})
        mayorzone.delete()
        return Response({'success': 'Mayor zone deleted'})
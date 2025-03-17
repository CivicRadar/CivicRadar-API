from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import User
from .models import Provinces, Cities, MayorCities
from Authentication.serializers import UserSerializer, UserIDSerializer
from .serializers import ProvinceSerializer, CitySerializer, MayorCitySerializer, MayorInfoSerializer
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
        city = Cities.objects.filter(id=request.data['CityID']).first()
        request.data['Type']='Mayor'
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        mayor = User.objects.filter(Email=request.data['Email']).first()
        mayorcity = MayorCities.objects.filter(User=mayor, City=city).first()
        if mayorcity is None:
            mayorcity = MayorCities(User=mayor, City=city)
            mayorcity.save()
            return Response({'success': 'Mayor city added!'})
        raise AuthenticationFailed('Only mayor added!')
        # return Response(serializer.data)

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
            raise AuthenticationFailed('Province not found!')

        mycities = Cities.objects.filter(Province=myprovince).all()
        serializer = CitySerializer(mycities, many=True)
        return Response(serializer.data)

class AddMayorCity(APIView):
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

        mayor = User.objects.filter(id=request.data['MayorID'], Type='Mayor').first()
        if mayor is None:
            raise AuthenticationFailed("Mayor not found!")
        mayorcity = MayorCities.objects.filter(User=mayor, City=city).first()
        if mayorcity is None:
            mayorcity = MayorCities(User=mayor, City=city)
            mayorcity.save()
            return Response({'success': 'Mayor city added!'})
        raise AuthenticationFailed('Mayor City already added!')

class ListMayorCity(APIView):
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

        mayorcities = MayorCities.objects.filter(User=mayor).all()
        serializer = MayorCitySerializer(mayorcities, many=True)
        return Response(serializer.data)

class RemoveMayorCity(APIView):
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

        mayor = User.objects.filter(id=request.data['MayorID'], Type='Mayor').first()
        if mayor is None:
            raise AuthenticationFailed("Mayor not found!")
        mayorcity = MayorCities.objects.filter(User=mayor, City=city).first()
        if mayorcity is None:
            raise AuthenticationFailed('Mayor city does not exist')
        mayorcity.delete()
        return Response({'success': 'Mayor city deleted'})

class ProvinceMayors(APIView):
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

        mayorcity = MayorCities.objects.filter(City__Province__id=request.data['ProvinceID']).values_list('User__id', flat=True)
        mayors = User.objects.filter(id__in=mayorcity, Type='Mayor').all()
        serializer = MayorInfoSerializer(mayors, many=True)
        return Response(serializer.data)

class CityMayors(APIView):
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

        mayorcity = MayorCities.objects.filter(City__id=request.data['CityID']).values_list('User__id', flat=True)
        mayors = User.objects.filter(id__in=mayorcity, Type='Mayor').all()
        serializer = MayorInfoSerializer(mayors, many=True)
        return Response(serializer.data)
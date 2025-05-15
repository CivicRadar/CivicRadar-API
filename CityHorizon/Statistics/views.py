from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from .serializers import MayorReportSerializer, CounterSerializer
from Authentication.models import User
import jwt
from django.conf import settings
from datetime import datetime
import uuid
import logging

# Set up logging
logger = logging.getLogger(__name__)

class MayorReportView(APIView):
    # def get(self, request):
    #     # Mayor can get the reports in their territory
    #     token = request.COOKIES.get('jwt')
    #
    #     if not token:
    #         raise AuthenticationFailed("Unauthenticated!")
    #
    #     try:
    #         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    #     except jwt.ExpiredSignatureError:
    #         raise AuthenticationFailed("Expired token!")
    #
    #     user = User.objects.filter(id=payload['id'], Type='Mayor').first()
    #     if user is None:
    #         raise AuthenticationFailed("User not found!")
    #
    #     # Filter reports by mayor
    #     reports = MayorReport.objects.filter(Mayor=user)
    #     serializer = MayorReportSerializer(reports, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Create a new report with charts
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

        # Serialize the saved instance for response
        response_serializer = MayorReportSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class Counter(APIView):
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

        serializer = CounterSerializer(user)
        return Response(serializer.data)
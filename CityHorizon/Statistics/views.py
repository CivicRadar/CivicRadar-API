from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from .models import MayorReport
from .serializers import MayorReportSerializer
from .utils import generate_and_save_charts
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

        # Generate charts
        report_id = str(uuid.uuid4())
        chart_files = generate_and_save_charts(report_id)

        # Create and save the report instance
        try:
            report = MayorReport(
                Mayor=user,
                report_date=datetime.now().date(),
                problem_status_pie_chart=chart_files['problem_status_pie_chart'],
                problem_type_bar_chart=chart_files['problem_type_bar_chart'],
                engagement_bar_chart=chart_files['engagement_bar_chart'],
                resolved_over_time_line_chart=chart_files['resolved_over_time_line_chart'],
                transition_time_bar_chart=chart_files['transition_time_bar_chart']
            )
            report.save()
            logger.debug(f"Report saved with ID: {report.id}")

            # Serialize the saved instance for response
            response_serializer = MayorReportSerializer(report)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error saving MayorReport: {str(e)}")
            return Response({"error": f"Failed to save report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
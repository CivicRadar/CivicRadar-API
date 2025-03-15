from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.core.mail import send_mail
from django.core import signing
from CityHorizon.settings import EMAIL_HOST_USER
from decouple import config
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from .serializers import UserSerializer, ResetPasswordRequestSerializer, SetNewPasswordSerializer
from rest_framework.response import Response
from .models import User
from django.core import signing
import jwt, datetime


class SignUp(APIView):
    def post(self, request):
        request.data['Type']='Citizen'
        data = { **request.data, "Verified": False }
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.data['Email']
        Typeof = serializer.data['Type']
        if User.objects.filter(Email=email, Type=Typeof).exists() is not None:
            # save it private using dotenv or environ
            token = signing.dumps({'email_address': email}, salt="my_verification_salt")
            absurl = f'http://127.0.0.1:8000/auth/email-verification/{token}/'

            from django.template import Template, Context
            user_name = serializer.data['FullName']

            subject = 'Verify Your Shahrsanj Account'

            email_body_template = Template("""
Dear {{ user_name }},

Click on this link for complete signning up:

{{ verification_code }}

This link will depreacated until 24 hours later

The Shahrsanj Team
""")
            context = Context({
                'user_name': user_name,
                'verification_code': absurl,
            })

            email_body = email_body_template.render(context)

            data = {
                'email_body': email_body,
                'to_email': email,
                'email_subject': subject
            }
            Util.send_email(data)
            return Response({'success': 'We have sent you a link to verify your email address'})
        else:
            return Response({'fail': 'there is a user with this email'})


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
            response.set_cookie(key='jwt', value=token, httponly=True, samesite=None, secure=config('COOKIE_SECURE', cast=bool))
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

class RequestPasswordReset(APIView):
    def post(self, request):
        email = request.data['Email']
        Typeof = request.data['Type']
        if User.objects.filter(Email=email, Type=Typeof).exists():
            user = User.objects.get(Email=email)
            ui64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            # Generate the frontend URL with uidb64 and token
            absurl = f'http://127.0.0.1:8000/auth/password-reset/{ui64}/{token}/'
            #
            from django.template import Template, Context
            user_name = user.FullName  # Replace with actual user name retrieval logic
            reset_link = absurl  # Replace with actual token generation logic

            # Email subject
            subject = 'Reset Your Shahrsanj Password'

            # Email body template as a string
            email_body_template = Template("""
Dear {{ user_name }},

We received a request to reset your password for your Shahrsanj account. If you did not make this request, please ignore this email.

To reset your password, please click the link below:

{{ reset_link }}

This link will expire in 24 hours for security reasons. If you do not reset your password within this time, you will need to submit a new request.

If you have any questions or need further assistance, please do not hesitate to contact our support team at support@shahrsanj.com.

Thank you for using Shahrsanj!

Best regards,

The Shahrsanj Team
             """)

            # Context data
            context = Context({
                'user_name': user_name,
                'reset_link': reset_link,
            })

            # Render the email body with the context
            email_body = email_body_template.render(context)

            #
            data = {
                'email_body': email_body,
                'to_email': email,
                'email_subject': 'Reset your password'
            }
            Util.send_email(data)
            return Response({'success': 'We have sent you a link to reset your password'})
        else:
            return Response({'fail': 'There is no such user'})


class PasswordTokenCheck(APIView):
    def get(self, request, ui64, token):
        try:
            id=smart_str(urlsafe_base64_decode(ui64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'fail': 'Invalid token'})
            return Response({'message':'Credentials valid', 'ui64':ui64, 'token':token})
        except DjangoUnicodeDecodeError:
            return Response({'fail': 'Invalid token'})

class SetNewPassword(APIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':'Password updated successfully'})

class EmailVerification(APIView):
    def get(self, request, token):
        try:
            data = signing.loads(token, salt="my_verification_salt", max_age=24 * 60 * 60)
            user = User.objects.get(Email=data['email_address'])
            user.save(update_fields={'Verified': True})
            return Response({'success': 'verified successfully'})
        except signing.BadSignature:
            return Response({'failed': 'bad signature'})
        except User.DoesNotExist:
            return Response({'failed': 'user not found'})

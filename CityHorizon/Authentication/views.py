from django.conf import settings
from django.http import HttpResponseBadRequest
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
from .serializers import UserSerializer, ResetPasswordRequestSerializer, SetNewPasswordSerializer, ProfileSerializer
from rest_framework.response import Response
from .models import User
from django.core import signing
import jwt, datetime


class SignUp(APIView):
    def post(self, request):
        request.data['Type'] = 'Citizen'
        email = request.data['Email']
        Typeof = 'Citizen'

        if User.objects.filter(Email=email).first() is None:
            # ایجاد توکن تأیید ایمیل
            token = signing.dumps({'email_address': email}, salt="my_verification_salt")

            # هدایت کاربر به فرانت‌اند React در localhost:5173
            frontend_url = f'{config("BASE_HTTP")}://{config("BASE_URL")}/verifyemail?token={token}'

            # ایجاد کاربر
            user = User(FullName=request.data['FullName'], Email=email, Type=Typeof)
            user.set_password(request.data['Password'])
            user.save()

            # قالب ایمیل
            from django.template import Template, Context
            user_name = user.FullName

            subject = 'Verify Your Shahrsanj Account'

            email_body_template = Template("""
Dear {{ user_name }},

Click on this link to complete your sign-up:

{{ verification_code }}

This link will expire in 24 hours.

The Shahrsanj Team
""")
            context = Context({
                'user_name': user_name,
                'verification_code': frontend_url,  # ارسال لینک جدید فرانت‌اند
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
            raise AuthenticationFailed('user with this Email already exists.')


class Login(APIView):
    def post(self, request):
        try:
            email = request.data['Email']
            password = request.data['Password']
            typeof = request.data['Type']
        except KeyError:
            return HttpResponseBadRequest("needs Email, Password and Type fields in request data")

        user = User.objects.filter(Email=email, Type=typeof).first()

        if user is not None and user.check_password(password):
            if user.Verified==False and user.Type=='Citizen':
                raise AuthenticationFailed('Please verify your account via Email.')

            payload = {
                'id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
                'iat': datetime.datetime.utcnow()
            }

            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            response = Response()
            response.set_cookie(key='jwt', value=token, httponly=True, samesite='None', secure=True)
            if user.Theme is not None:
                response.set_cookie(key='theme', value=user.Theme)

            response.data = {'jwt': token}
            return response
        raise AuthenticationFailed('your email or password is incorrect')

class Logout(APIView):
    def get(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'You have been logged out.'
        }

        return response

    def delete(self, request):
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
        user.delete()
        return Response({'message': 'Your account has been deleted.'})

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

        serializer = ProfileSerializer(user)
        return Response(serializer.data)

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

        profile_serializer = ProfileSerializer(data=request.data)
        try:
            profile_serializer.is_valid()
            user.FullName = profile_serializer.data['FullName']
            picture = request.FILES.get('Picture')
            if picture:
                user.Picture = picture
            # در غیر این صورت، فایلی نیومده، عکس قبلی بمونه
            user.save()
            serializer = ProfileSerializer(user)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            return HttpResponseBadRequest(e.detail)

    def delete(self, request):
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
        user.Picture = None
        user.save()
        serializer = ProfileSerializer(user)
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
            absurl = f'{config("BASE_HTTP")}://{config("BASE_URL")}/auth/password-reset/{ui64}/{token}/'
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
            raise AuthenticationFailed('There is no such user')


class PasswordTokenCheck(APIView):
    def get(self, request, ui64, token):
        try:
            id=smart_str(urlsafe_base64_decode(ui64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('Invalid token')
            return Response({'message':'Credentials valid', 'ui64':ui64, 'token':token})
        except DjangoUnicodeDecodeError:
            raise AuthenticationFailed('Invalid token')

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
            user.Verified=True
            user.save()
            return Response({'success': 'verified successfully'})
        except signing.BadSignature:
            raise AuthenticationFailed('bad signature')
        except User.DoesNotExist:
            raise AuthenticationFailed('user not found')

class SetTheme(APIView):
    def post(self, request):
        try:
            token = request.COOKIES.get('jwt')
            new_theme = request.data['theme']
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.filter(id=payload['id']).first()
            if user is None:
                raise AuthenticationFailed("User not found!")
            user.Theme = new_theme
            user.save()
            response = Response({"success": "theme changed successfully"})
            response.set_cookie(key="theme", value=user.Theme)
            return response
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")
        except KeyError:
            return HttpResponseBadRequest("needs theme field in request data")

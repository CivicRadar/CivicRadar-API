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

            # هدایت کاربر به فرانت‌اند React
            frontend_url = f'{config("BASE_HTTP")}://{config("BASE_URL")}/verifyemail?token={token}'

            # ایجاد کاربر
            user = User(FullName=request.data['FullName'], Email=email, Type=Typeof)
            user.set_password(request.data['Password'])
            user.save()

            # قالب ایمیل
            from django.template import Template, Context
            user_name = user.FullName

            # Email subject
            subject = 'حساب شهرسنج خود را تایید کنید'

            # HTML email body template
            html_email_body_template = Template("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تایید حساب کاربری شهرسنج</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap" rel="stylesheet">
</head>
<body style="margin: 0; padding: 0; font-family: 'Vazirmatn', Arial, sans-serif; background-color: #f4f4f4;">
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; margin: 20px auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <tr>
            <td style="padding: 40px 30px; text-align: right;">
                <h1 style="color: #333333; font-size: 24px; margin: 0 0 20px;">!به شهرسنج خوش آمدید</h1>
                <p style="color: #555555; font-size: 16px; line-height: 1.5; margin: 0 0 20px;">
                    ،{{ user_name }} عزیز
                </p>
                <p style="color: #555555; font-size: 16px; line-height: 1.5; margin: 0 0 20px;">
                    از ثبت‌نام شما در شهرسنج متشکریم! برای تکمیل ثبت‌نام، لطفاً با کلیک بر روی دکمه زیر آدرس ایمیل خود را تایید کنید:
                </p>
                <div style="text-align: center;">
                    <a href="{{ verification_code }}" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">تایید ایمیل</a>
                </div>
                <p style="color: #555555; font-size: 14px; line-height: 1.5; margin: 20px 0 0;">
                    .این لینک تا ۲۴ ساعت معتبر است. در صورت عدم تایید ایمیل در این مدت، لازم است مجدداً ثبت‌نام کنید
                </p>
                <p style="color: #555555; font-size: 14px; line-height: 1.5; margin: 20px 0 0;">
                    اگر شما در شهرسنج حساب کاربری ایجاد نکرده‌اید، لطفاً این ایمیل را نادیده بگیرید.
                </p>
                <p style="color: #555555; font-size: 14px; line-height: 1.5; margin: 20px 0 0;">
                    در صورت داشتن هرگونه سؤال، می‌توانید با تیم پشتیبانی ما از طریق <a href="mailto:support@shahrsanj.com" style="color: #007bff; text-decoration: none;">support@shahrsanj.com</a> در تماس باشید.
                </p>
                <p style="color: #555555; font-size: 14px; line-height: 1.5; margin: 10px 0 0;">
                    ،با احترام<br>تیم شهرسنج
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
            """)

            # Plain text email body template (fallback)
            plain_email_body_template = Template("""
Dear {{ user_name }},

Thank you for signing up for a Shahrsanj account! To complete your registration, please verify your email address by clicking the link below:

{{ verification_code }}

This link will expire in 24 hours. If you do not verify your email within this time, you will need to sign up again.

If you did not create an account with Shahrsanj, please ignore this email.

If you have any questions, feel free to contact our support team at support@shahrsanj.com.

Best regards,

The Shahrsanj Team
            """)

            # Context data
            context = Context({
                'user_name': user_name,
                'verification_code': frontend_url,
            })

            # Render both HTML and plain text email bodies
            html_email_body = html_email_body_template.render(context)
            plain_email_body = plain_email_body_template.render(context)

            # Email data for sending
            data = {
                'email_body': plain_email_body,  # Plain text body
                'html_email_body': html_email_body,  # HTML body
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

        user.FullName = request.data.get('FullName', user.FullName)

        picture = request.FILES.get('Picture')
        if picture:
            user.Picture = picture
        # در غیر این صورت، فایلی نیومده، عکس قبلی بمونه

        user.save()
        serializer = ProfileSerializer(user)
        return Response(serializer.data)

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

            from django.template import Template, Context
            user_name = user.FullName

            # Email subject
            subject = 'رمز عبور حساب شهرسنج خود را بازنشانی کنید'

            # HTML email body template
            html_email_body_template = Template("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بازنشانی رمز عبور شهرسنج</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
</head>
<body style="margin: 0; padding: 0; font-family: 'Vazirmatn', Arial, sans-serif; background-color: #f4f4f4;">
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; margin: 20px auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <tr>
            <td style="padding: 40px 30px; text-align: right;">
                <h1 style="color: #333333; font-size: 24px; margin: 0 0 20px;">بازنشانی رمز عبور شهرسنج</h1>
                <p style="color: #555555; font-size: 16px; line-height: 1.8; margin: 0 0 20px;">،{{ user_name }} عزیز</p>
                <p style="color: #555555; font-size: 16px; line-height: 1.8; margin: 0 0 20px;">.درخواستی برای بازنشانی رمز عبور حساب کاربری شما در شهرسنج دریافت کردیم. اگر شما این درخواست را ارسال نکرده‌اید، لطفاً این ایمیل را نادیده بگیرید</p>
                <p style="color: #555555; font-size: 16px; line-height: 1.8; margin: 0 0 20px;">:برای بازنشانی رمز عبور خود، لطفاً روی دکمه زیر کلیک کنید</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{ reset_link }}" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">بازنشانی رمز عبور</a>
                </div>
                <p style="color: #555555; font-size: 14px; line-height: 1.8; margin: 20px 0 0;">.این لینک به دلایل امنیتی تا ۲۴ ساعت معتبر است. اگر در این مدت رمز عبور خود را بازنشانی نکنید، باید درخواست جدیدی ارسال کنید</p>
                <p style="color: #555555; font-size: 14px; line-height: 1.8; margin: 20px 0 0;">در صورت داشتن هرگونه سؤال یا نیاز به راهنمایی بیشتر، لطفاً با تیم پشتیبانی ما از طریق <a href="mailto:support@shahrsanj.com" style="color: #007bff; text-decoration: none;">support@shahrsanj.com</a> .تماس بگیرید</p>
                <p style="color: #555555; font-size: 14px; line-height: 1.8; margin: 20px 0 0;">!با تشکر از اینکه از شهرسنج استفاده می‌کنید</p>
                <p style="color: #555555; font-size: 14px; line-height: 1.8; margin: 10px 0 0;">،با احترام<br>تیم شهرسنج</p>
            </td>
        </tr>
    </table>
</body>
</html>
            """)

            # Plain text email body template (fallback)
            plain_email_body_template = Template("""
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
                'reset_link': absurl,
            })

            # Render both HTML and plain text email bodies
            html_email_body = html_email_body_template.render(context)
            plain_email_body = plain_email_body_template.render(context)

            # Email data for sending
            data = {
                'email_body': plain_email_body,  # Plain text body
                'html_email_body': html_email_body,  # HTML body
                'to_email': email,
                'email_subject': subject
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

from django.core.mail import EmailMessage
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework import serializers


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']]
        )
        email.send()

    @staticmethod
    def is_contain_required_fields(data, required_fields, raise_exception=True):
        if any(field not in data.keys() for field in required_fields):
            if raise_exception:
                raise serializers.ValidationError(f"all of these keys should exist in data: {required_fields}")
            else:
                return False

class UnAuthorizedResponse(Response):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, status=status.HTTP_401_UNAUTHORIZED)

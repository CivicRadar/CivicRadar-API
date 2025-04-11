from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.response import Response


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']]
        )
        email.send()

class UnAuthorizedResponse(Response):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, status=status.HTTP_401_UNAUTHORIZED)

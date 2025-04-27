from django.conf import settings
from django.core.mail import EmailMultiAlternatives


class Util:
    @staticmethod
    def send_email(data):
        subject = data['email_subject']
        plain_message = data['email_body']
        html_message = data.get('html_email_body')
        to_email = data['to_email']

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email]
        )
        if html_message:
            email.attach_alternative(html_message, "text/html")
        email.send()
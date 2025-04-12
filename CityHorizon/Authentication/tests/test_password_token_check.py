import datetime
from django.conf import settings
import jwt
from django.test import TestCase, tag
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.exceptions import AuthenticationFailed
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes, smart_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse

from Authentication.tests.utilities import create_user

User = get_user_model()

@tag('password_token_check')
class PasswordTokenCheckTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            Email='test@example.com',
            Password='testpass123',
            FullName='Test User',
            Type='Citizen',
            Verified=True
        )
        self.generator = PasswordResetTokenGenerator()
        self.uidb64 = urlsafe_base64_encode(smart_bytes(self.user.id))
        self.valid_token = self.generator.make_token(self.user)

    # Helper method to generate URL
    def get_url(self, uidb64, token):
        return reverse('password-reset-confirmed', args=[uidb64, token])

    def __assert_unauthenticated_response(self, response, detail_value):
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'], detail_value)

    # Test valid credentials
    def test_valid_token_and_uid(self):
        url = self.get_url(self.uidb64, self.valid_token)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Credentials valid')
        self.assertEqual(response.data['ui64'], self.uidb64)
        self.assertEqual(response.data['token'], self.valid_token)

    # Test invalid token
    def test_invalid_token(self):
        invalid_token = self.valid_token[:-1] + 'x'  # Corrupt last character
        url = self.get_url(self.uidb64, invalid_token)

        response = self.client.get(url)

        self.__assert_unauthenticated_response(response, 'Invalid token')

    # Test invalid uidb64 encoding
    def test_invalid_uidb64(self):
        invalid_uidb64 = 'invalid_uid!!'  # Invalid base64 characters
        url = self.get_url(invalid_uidb64, self.valid_token)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid token')

    # # Test expired token (requires time manipulation)
    # def test_expired_token(self):
    #     # Create token with past timestamp
    #     expired_payload = {
    #         'id': self.user.id,
    #         'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    #     }
    #     expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm='HS256')
        
    #     url = self.get_url(self.uidb64, expired_token)
    #     with self.assertRaises(AuthenticationFailed) as cm:
    #         self.client.get(url)
            
    #     self.assertEqual(str(cm.exception.detail), 'Invalid token')
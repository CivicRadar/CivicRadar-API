from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt
import datetime

from Authentication.tests.utilities import create_user

User = get_user_model()

class SetThemeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/auth/set-theme/'
        
        # Create test user
        self.user = create_user(
            Email='test@example.com',
            Password='testpass123',
            FullName='Test User',
            Type='Citizen',
            Theme='light'
        )
        
        # Generate valid JWT
        self.valid_payload = {
            'id': self.user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow()
        }
        self.valid_token = jwt.encode(self.valid_payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Generate expired JWT
        self.expired_payload = {
            'id': self.user.id,
            'exp': datetime.datetime.utcnow() - datetime.timedelta(seconds=1),
            'iat': datetime.datetime.utcnow()
        }
        self.expired_token = jwt.encode(self.expired_payload, settings.SECRET_KEY, algorithm='HS256')

    def test_successful_theme_update(self):
        # Set cookie and send request
        self.client.cookies['jwt'] = self.valid_token
        response = self.client.post(self.url, {'theme': 'dark'}, format='json')

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], 'theme changed successfully')

        # Check database update
        self.user.refresh_from_db()
        self.assertEqual(self.user.Theme, 'dark')

        # Check cookie set
        self.assertEqual(response.cookies['theme'].value, 'dark')

    def test_missing_theme_field(self):
        self.client.cookies['jwt'] = self.valid_token
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('needs theme field', response.content.decode())

    # def test_expired_token(self):
    #     self.client.cookies['jwt'] = self.expired_token
    #     with self.assertRaises(AuthenticationFailed) as cm:
    #         self.client.post(self.url, {'theme': 'dark'}, format='json')
        
    #     self.assertEqual(str(cm.exception.detail), 'Expired token!')

    # def test_invalid_user(self):
    #     # Create valid token for non-existent user
    #     payload = {
    #         'id': 9999,  # Non-existent ID
    #         'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    #         'iat': datetime.datetime.utcnow()
    #     }
    #     invalid_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
    #     self.client.cookies['jwt'] = invalid_token
    #     with self.assertRaises(AuthenticationFailed) as cm:
    #         self.client.post(self.url, {'theme': 'dark'}, format='json')
        
    #     self.assertEqual(str(cm.exception.detail), 'User not found!')

    # def test_unauthenticated_request(self):
    #     # No JWT cookie set
    #     response = self.client.post(self.url, {'theme': 'dark'}, format='json')
    #     self.assertEqual(response.status_code, 401)

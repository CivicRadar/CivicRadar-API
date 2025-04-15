from django.test import TestCase, tag
from rest_framework.test import APIClient
from Authentication.models import User
from django.conf import settings
import jwt
import datetime
import json

from Authentication.tests.utilities import create_user

@tag('logout')
class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/auth/logout/'  # Update with your actual URL
        
        # Create test user
        self.user = create_user(
            Email='test@example.com',
            Password='testpass123',
            FullName='Test User',
            Type='Citizen',
            Verified=True
        )
        
        # Generate valid token
        self.valid_payload = {
            'id': self.user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow()
        }
        self.valid_token = jwt.encode(self.valid_payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Generate expired token
        self.expired_payload = {
            'id': self.user.id,
            'exp': datetime.datetime.utcnow() - datetime.timedelta(seconds=1),
            'iat': datetime.datetime.utcnow()
        }
        self.expired_token = jwt.encode(self.expired_payload, settings.SECRET_KEY, algorithm='HS256')

    # GET method tests
    def test_successful_logout(self):
        # Simulate logged-in user with cookie
        self.client.cookies['jwt'] = self.valid_token
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'You have been logged out.')
        
        # Check cookie deletion
        self.assertIn('jwt', response.cookies)
        self.assertEqual(response.cookies['jwt'].value, '')
        self.assertTrue(response.cookies['jwt']['expires'] == 'Thu, 01 Jan 1970 00:00:00 GMT')

    # DELETE method tests
    def test_delete_without_token(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content.decode('utf-8'))['detail'], 'Unauthenticated!')

    def test_delete_with_expired_token(self):
        self.client.cookies['jwt'] = self.expired_token

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content.decode('utf-8'))['detail'], 'Expired token!')

    def test_successful_account_deletion(self):
        self.client.cookies['jwt'] = self.valid_token

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Your account has been deleted.')
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_nonexistent_user(self):
        # Delete user first
        self.user.delete()

        self.client.cookies['jwt'] = self.valid_token

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content.decode('utf-8'))['detail'], 'User not found!')

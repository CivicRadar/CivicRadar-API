from django.test import TestCase, tag
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from django.conf import settings
import jwt
import datetime

from Authentication.tests.utilities import create_user

@tag('profile_view')
class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/auth/profile/'
        
        # Create test user
        self.user = create_user(
            Email='test@example.com',
            Password='testpass123',
            FullName='Original Name',
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

    # Helper methods
    def __set_auth_cookie(self, token):
        self.client.cookies['jwt'] = token

    def __assert_unauthenticated_response(self, response, detail_value):
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'], detail_value)

    # GET method tests
    def test_get_unauthenticated(self):
        response = self.client.get(self.url)

        self.__assert_unauthenticated_response(response, 'Unauthenticated!')

    def test_get_expired_token(self):
        self.__set_auth_cookie(self.expired_token)
        response = self.client.get(self.url)
        self.__assert_unauthenticated_response(response, 'Expired token!')

    def test_get_valid_profile(self):
        self.__set_auth_cookie(self.valid_token)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['Email'], 'test@example.com')
        self.assertEqual(response.data['FullName'], 'Original Name')

    # POST method tests
    def test_post_unauthenticated(self):
        response = self.client.post(self.url, {'FullName': 'New Name'})
        self.__assert_unauthenticated_response(response, 'Unauthenticated!')

    def test_post_missing_required_field(self):
        self.__set_auth_cookie(self.valid_token)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('utf-8'), "all of these keys should exist in data: ['FullName']")

    def test_post_successful_update(self):
        self.__set_auth_cookie(self.valid_token)
        new_picture = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")

        response = self.client.post(self.url, {
            'FullName': 'Updated Name',
            'Picture': new_picture
        }, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.FullName, 'Updated Name')
        self.assertTrue(self.user.Picture.name.endswith('test.jpg'))

    def test_post_partial_update(self):
        self.__set_auth_cookie(self.valid_token)
        response = self.client.post(self.url, {
            'FullName': 'Partial Update'
        })
        
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.FullName, 'Partial Update')
        self.assertEqual(self.user.Picture.name, '')  # Verify picture wasn't changed

    def test_post_invalid_user(self):
        self.user.delete()
        self.__set_auth_cookie(self.valid_token)

        response = self.client.post(self.url, {'FullName': 'New Name'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error'], 'User not found!')

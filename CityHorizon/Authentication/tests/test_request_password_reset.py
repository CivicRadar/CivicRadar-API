from django.test import TestCase, tag
from rest_framework.test import APIClient
from unittest.mock import patch
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from Authentication.tests.utilities import create_user

@tag('request_password_reset')
class RequestPasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/auth/request-reset-email/'
        
        # Create test user
        self.user = create_user(
            Email='user@example.com',
            Password='testpass123',
            FullName='Test User',
            Type='Citizen',
            Verified=True
        )

    def test_successful_password_reset_request(self):
        with patch('Authentication.views.Util.send_email') as mock_send_email:
            response = self.client.post(
                self.url,
                {'Email': 'user@example.com', 'Type': 'Citizen'},
                format='json'
            )

            # Test response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.data['success'],
                'We have sent you a link to reset your password'
            )

            # Test email generation
            self.assertTrue(mock_send_email.called)
            email_data = mock_send_email.call_args[0][0]
            
            # Validate email content
            self.assertIn(self.user.FullName, email_data['email_body'])
            self.assertIn('support@shahrsanj.com', email_data['email_body'])
            
            # Validate token generation
            uid = urlsafe_base64_encode(smart_bytes(self.user.id))
            token = PasswordResetTokenGenerator().make_token(self.user)
            self.assertIn(uid, email_data['email_body'])
            self.assertIn(token, email_data['email_body'])

    def test_nonexistent_user(self):
        response = self.client.post(
            self.url,
            {'Email': 'nonexistent@example.com', 'Type': 'Citizen'},
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {'error': 'There is no such user'})

    def test_invalid_user_type(self):
        response = self.client.post(
            self.url,
            {'Email': 'user@example.com', 'Type': 'Mayor'},
            format='json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {'error': 'There is no such user'})

    def test_missing_fields(self):
        test_cases = [
            {'Type': 'Citizen'},  # Missing Email
            {'Email': 'user@example.com'},  # Missing Type
            {}  # Both missing
        ]

        for data in test_cases:
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertIn(response.content.decode('utf-8'), "all of these keys should exist in data: ['Email', 'Type']")

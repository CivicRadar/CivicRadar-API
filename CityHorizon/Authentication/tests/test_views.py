from django.test import TestCase
from django.core import signing
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework.exceptions import AuthenticationFailed
from Authentication.models import User
from unittest.mock import patch

class SignUpTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/auth/signup/'  # Update with your actual URL
        self.valid_data = {
            'FullName': 'Test User',
            'Email': 'test@example.com',
            'Password': 'securepassword123'
        }
        
    def tearDown(self):
        User.objects.all().delete()

    @patch('Authentication.utils.Util.send_email')  # Mock email sending
    def test_successful_signup(self, mock_send_email):
        response = self.client.post(self.url, self.valid_data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], 'We have sent you a link to verify your email address')
        
        # Check user creation
        user = User.objects.first()
        self.assertEqual(user.Email, 'test@example.com')
        self.assertEqual(user.Type, 'Citizen')
        self.assertTrue(user.check_password('securepassword123'))
        
        # # Check verification token
        # token = signing.dumps({'email_address': 'test@example.com'}, salt="my_verification_salt")
        # self.assertTrue(mock_send_email.called)
        # print(mock_send_email.call_args[1])
        # email_body = mock_send_email.call_args[1]['data']['email_body']
        # self.assertIn(token, email_body)

    def test_duplicate_email_signup(self):
        # Create existing user first
        user = User(FullName='Existing User', Email='test@example.com', Type='Citizen')
        user.set_password('existingpass')
        user.save()

        response = self.client.post(self.url, self.valid_data, format='json')
        
        # Check error response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode('utf-8'),
            'user with this Email already exists.'
        )

    # def test_missing_required_fields(self):
    #     test_cases = [
    #         {'Email': 'test@example.com', 'Password': 'pass'},  # Missing FullName
    #         {'FullName': 'Test', 'Password': 'pass'},           # Missing Email
    #         {'FullName': 'Test', 'Email': 'test@example.com'}   # Missing Password
    #     ]
        
    #     for data in test_cases:
    #         response = self.client.post(self.url, data, format='json')
    #         self.assertEqual(response.status_code, 400)

    # @patch('Authentication.utils.Util.send_email')
    # def test_verification_link_generation(self, mock_send_email):
    #     with self.settings(
    #         BASE_HTTP='https',
    #         BASE_URL='frontend.example.com'
    #     ):
    #         response = self.client.post(self.url, self.valid_data, format='json')
            
    #         # Verify link construction
    #         token = signing.dumps({'email_address': 'test@example.com'}, salt="my_verification_salt")
    #         expected_url = f'https://frontend.example.com/verifyemail?token={token}'
            
    #         email_body = mock_send_email.call_args[1]['data']['email_body']
    #         self.assertIn(expected_url, email_body)

    # @patch('Authentication.utils.Util.send_email')
    # def test_email_template_content(self, mock_send_email):
    #     self.client.post(self.url, self.valid_data, format='json')
        
    #     email_data = mock_send_email.call_args[1]['data']
    #     self.assertEqual(email_data['email_subject'], 'Verify Your Shahrsanj Account')
    #     self.assertIn('Dear Test User', email_data['email_body'])
    #     self.assertIn('The Shahrsanj Team', email_data['email_body'])


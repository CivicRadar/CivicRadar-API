import json
from django.test import TestCase, tag
from django.core import signing
from rest_framework.test import APIClient
from rest_framework.exceptions import AuthenticationFailed
from Authentication.models import User
from unittest.mock import patch
from decouple import config
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
import datetime

from Authentication.tests.utilities import create_user

@tag('signup')
class SignUpTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/auth/signup/'  # Update with your actual URL
        self.valid_data = {
            'FullName': 'Test User',
            'Email': 'test@example.com',
            'Password': 'securepassword123',
            'Type': 'Citizen'
        }
        
    def tearDown(self):
        User.objects.all().delete()

    @tag('unstable')
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
        
        # Check verification token
        token = signing.dumps({'email_address': 'test@example.com'}, salt="my_verification_salt")
        self.assertTrue(mock_send_email.called)
        email_body = mock_send_email.call_args[0][0]['email_body']
        self.assertIn(token, email_body)

    def test_duplicate_email_signup(self):
        # Create existing user first
        create_user('test@example.com', 'existingpass', 'Existing User', 'Citizen')

        response = self.client.post(self.url, self.valid_data, format='json')
        
        # Check error response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode('utf-8'),
            'user with this Email already exists.'
        )

    def test_missing_required_fields(self):
        test_cases = [
            {'Email': 'test@example.com', 'Password': 'pass'},  # Missing FullName
            {'FullName': 'Test', 'Password': 'pass'},           # Missing Email
            {'FullName': 'Test', 'Email': 'test@example.com'}   # Missing Password
        ]
        
        for data in test_cases:
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, 400)

    @tag('unstable')
    @patch('Authentication.utils.Util.send_email')
    def test_verification_link_generation(self, mock_send_email):
        self.client.post(self.url, self.valid_data, format='json')

        # Verify link construction
        token = signing.dumps({'email_address': 'test@example.com'}, salt="my_verification_salt")
        expected_url = f'{config("BASE_HTTP")}://{config("BASE_URL")}/verifyemail?token={token}'

        email_body = mock_send_email.call_args[0][0]['email_body']
        self.assertIn(expected_url, email_body)

    @patch('Authentication.utils.Util.send_email')
    def test_email_template_content(self, mock_send_email):
        self.client.post(self.url, self.valid_data, format='json')
        
        email_data = mock_send_email.call_args[0][0]
        self.assertEqual(email_data['email_subject'], 'Verify Your Shahrsanj Account')
        self.assertIn('Dear Test User', email_data['email_body'])
        self.assertIn('The Shahrsanj Team', email_data['email_body'])

User = get_user_model()

@tag('login')
class LoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/auth/login/'  # Update with your actual endpoint
        
        # Create test users
        self.verified_citizen = create_user(
            Email='verified@example.com',
            Password='citizen123',
            FullName='Verified Citizen',
            Type='Citizen',
            Verified=True
        )
        
        self.unverified_citizen = create_user(
            Email='unverified@example.com',
            Password='citizen123',
            FullName='Unverified Citizen',
            Type='Citizen',
            Verified=False
        )
        
        self.mayor = create_user(
            Email='mayor@city.gov',
            Password='mayor123',
            FullName='City Mayor',
            Type='Mayor'
        )

    # Helper method for JWT validation
    def decode_token(self, token):
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

    # Test Cases
    def test_missing_required_fields(self):
        test_cases = [
            {'Password': 'pass', 'Type': 'Citizen'},        # Missing Email
            {'Email': 'test@example.com', 'Type': 'Citizen'}, # Missing Password
            {'Email': 'test@example.com', 'Password': 'pass'} # Missing Type
        ]
        
        for data in test_cases:
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('needs Email, Password and Type fields', response.content.decode())

    def test_invalid_credentials(self):
        # Non-existent user
        response = self.client.post(self.url, {
            'Email': 'nonexistent@example.com',
            'Password': 'pass',
            'Type': 'Citizen'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('email or password is incorrect', response.content.decode())

        # Wrong password
        response = self.client.post(self.url, {
            'Email': 'verified@example.com',
            'Password': 'wrongpass',
            'Type': 'Citizen'
        })
        self.assertEqual(response.status_code, 401)

    def test_unverified_citizen(self):
        response = self.client.post(self.url, {
            'Email': 'unverified@example.com',
            'Password': 'citizen123',
            'Type': 'Citizen'
        })
        self.assertEqual(response.status_code, 403)
        self.assertIn('Please verify your account via Email', response.content.decode())

    def test_successful_citizen_login(self):
        response = self.client.post(self.url, {
            'Email': 'verified@example.com',
            'Password': 'citizen123',
            'Type': 'Citizen'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Verify JWT in response
        self.assertIn('jwt', response.data)
        token = response.data['jwt']
        decoded = self.decode_token(token)
        
        # Validate token payload
        self.assertEqual(decoded['id'], self.verified_citizen.id)
        self.assertAlmostEqual(
            decoded['exp'],
            (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).timestamp(),
            delta=5  # Allow 5 seconds difference
        )
        
        # Verify cookies
        jwt_cookie = response.cookies.get('jwt')
        self.assertTrue(jwt_cookie)
        self.assertEqual(jwt_cookie.value, token)
        self.assertTrue(jwt_cookie['httponly'])
        self.assertTrue(jwt_cookie['secure'])
        self.assertEqual(jwt_cookie['samesite'], 'None')

    def test_successful_mayor_login(self):
        response = self.client.post(self.url, {
            'Email': 'mayor@city.gov',
            'Password': 'mayor123',
            'Type': 'Mayor'
        })

        self.assertEqual(response.status_code, 200)
        decoded = self.decode_token(response.data['jwt'])
        self.assertEqual(decoded['id'], self.mayor.id)

    def test_theme_cookie(self):
        # Create user with theme preference
        create_user(
            Email='themeuser@example.com',
            Password='theme123',
            FullName='Theme User',
            Type='Citizen',
            Verified=True,
            Theme='dark'
        )

        response = self.client.post(self.url, {
            'Email': 'themeuser@example.com',
            'Password': 'theme123',
            'Type': 'Citizen'
        })

        theme_cookie = response.cookies.get('theme')
        self.assertTrue(theme_cookie)
        self.assertEqual(theme_cookie.value, 'dark')

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

    # def test_delete_with_expired_token(self):
    #     self.client.cookies['jwt'] = self.expired_token
        
    #     with self.assertRaises(AuthenticationFailed) as cm:
    #         self.client.delete(self.url)
        
    #     self.assertEqual(str(cm.exception.detail), 'Expired token!')

    # def test_successful_account_deletion(self):
    #     self.client.cookies['jwt'] = self.valid_token
        
    #     response = self.client.delete(self.url)
        
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['message'], 'Your account has been deleted.')
    #     self.assertFalse(User.objects.filter(id=self.user.id).exists())

    # def test_delete_nonexistent_user(self):
    #     # Delete user first
    #     self.user.delete()
        
    #     self.client.cookies['jwt'] = self.valid_token
        
    #     with self.assertRaises(AuthenticationFailed) as cm:
    #         self.client.delete(self.url)
        
    #     self.assertEqual(str(cm.exception.detail), 'User not found!')

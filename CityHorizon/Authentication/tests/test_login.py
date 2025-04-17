from django.test import TestCase, tag
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
import datetime

from Authentication.tests.utilities import create_user

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


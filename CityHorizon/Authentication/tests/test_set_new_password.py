from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse

from Authentication.tests.utilities import create_user

User = get_user_model()

class SetNewPasswordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('password-reset-complete')  # Update with your URL name
        self.user = create_user(
            Email='user@example.com',
            Password='oldpassword123',
            FullName='Test User',
            Type='Citizen',
            Verified=True
        )
        self.generator = PasswordResetTokenGenerator()
        
        # Generate valid reset credentials
        self.valid_uid = urlsafe_base64_encode(smart_bytes(self.user.id))
        self.valid_token = self.generator.make_token(self.user)
        
        # Base valid data
        self.valid_data = {
            'ui64': self.valid_uid,
            'token': self.valid_token,
            'Password': 'newSecurePassword123!',
            'ConfirmPassword': 'newSecurePassword123!'
        }

    # Success case
    def test_valid_password_reset(self):
        response = self.client.patch(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], 'Password updated successfully')
        
        # Verify password actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newSecurePassword123!'))

    # Failure cases
    def test_password_mismatch(self):
        data = {**self.valid_data, 'ConfirmPassword': 'differentPassword456!'}
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, 403)
        self.assertIn('Passwords do not match', str(response.content))

    def test_invalid_token(self):
        data = {**self.valid_data, 'token': 'invalid-token-123'}
        response = self.client.patch(self.url, data, format='json')
        
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {"detail":"The reset link is invalid"})

    # def test_invalid_uid(self):
    #     data = {**self.valid_data, 'uid': 'invalid_uid!!'}
    #     response = self.client.patch(self.url, data, format='json')
        
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn('Invalid user ID', str(response.content))

    # def test_weak_password(self):
    #     data = {**self.valid_data, 
    #            'password': '1234',
    #            'ConfirmPassword': '1234'}
    #     response = self.client.patch(self.url, data, format='json')
        
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn('This password is too short', str(response.content))

    # def test_expired_token(self):
    #     # Create another user with expired token
    #     expired_user = create_user(
    #         Email='expired@example.com',
    #         Password='testpass'
    #     )
    #     expired_uid = urlsafe_base64_encode(smart_bytes(expired_user.id))
    #     expired_token = self.generator.make_token(expired_user)
        
    #     # Invalidate token by changing password
    #     expired_user.set_password('newpassword')
    #     expired_user.save()
        
    #     data = {
    #         'uid': expired_uid,
    #         'token': expired_token,
    #         'password': 'newPass123!',
    #         'ConfirmPassword': 'newPass123!'
    #     }
    #     response = self.client.patch(self.url, data, format='json')
        
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn('Invalid token', str(response.content))
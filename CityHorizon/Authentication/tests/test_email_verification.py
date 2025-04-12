from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core import signing
from django.core.signing import b62_encode
from django.urls import reverse
from django.core.signing import TimestampSigner
import time

from Authentication.tests.utilities import create_user

User = get_user_model()


class CustomTimestampSigner(TimestampSigner):
    def __init__(self, custom_time=None, *args, **kwargs):
        """
        custom_time: a datetime.datetime instance specifying the
                     timestamp that should be embedded.
        If custom_time is None, the normal current time is used.
        """
        self.custom_time = custom_time
        super().__init__(*args, **kwargs)

    def timestamp(self):
        """
        Return a custom timestamp (in seconds since epoch) if provided,
        otherwise use the current system time.
        """
        if self.custom_time:
            # Convert the provided datetime to seconds since epoch.
            return b62_encode(int(self.custom_time))
        return b62_encode(int(time.time()))


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            Email='test@example.com',
            Password='testpass',
            FullName='Test User',
            Type='Citizen',
            Verified=False
        )

        # Generate valid token with timestamp
        signer = CustomTimestampSigner(custom_time=time.time(), salt='my_verification_salt')
        self.valid_token = signing.dumps({'email_address': self.user.Email}, salt="my_verification_salt")


        # Token for non-existent user
        self.non_user_token = signer.sign('nonexistent@example.com')

        # Generate expired token (25 hours old)
        signer = CustomTimestampSigner(custom_time=time.time() - (25 * 3600), salt='my_verification_salt')
        self.expired_token = signer.sign(self.user.Email)

        # Generate invalid token
        self.invalid_token = self.valid_token[:-1] + 'x'


    def test_valid_token(self):
        url = reverse('sign-up-email-verification', args=[self.valid_token])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], 'verified successfully')
        self.user.refresh_from_db()
        self.assertTrue(self.user.Verified)

    def test_expired_token(self):
        url = reverse('sign-up-email-verification', args=[self.expired_token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {'detail': 'bad signature'})

    def test_invalid_token(self):
        url = reverse('sign-up-email-verification', args=[self.invalid_token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {'detail': 'bad signature'})

    def test_user_not_found(self):
        url = reverse('sign-up-email-verification', args=[self.non_user_token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {'detail': 'bad signature'})

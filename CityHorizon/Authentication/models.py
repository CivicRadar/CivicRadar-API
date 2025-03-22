from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    account_type = [
        ("Admin", "Admin"),
        ("Mayor", "Mayor"),
        ("Citizen", "Citizen"),
    ]

    FullName = models.CharField(max_length=255)
    Email = models.EmailField(unique=True)
    Password = models.CharField(max_length=255)
    Type = models.CharField(max_length=20, choices=account_type, blank=False, null=False, default="Citizen")
    LastCooperation = models.DateField(auto_now=False, auto_now_add=False, default=None, null=True, blank=True)
    Verified = models.BooleanField(default=False)
    Picture = models.ImageField(upload_to="Profile_Pictures", null=True, blank=True)
    username = None
    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = []
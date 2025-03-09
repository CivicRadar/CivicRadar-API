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
    username = None
    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = []
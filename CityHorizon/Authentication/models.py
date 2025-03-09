from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    FullName = models.CharField(max_length=255)
    Email = models.EmailField(unique=True)
    Password = models.CharField(max_length=255)
    username = None
    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = []
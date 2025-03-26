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

class Provinces(models.Model):
    Name = models.CharField(max_length=40, unique=True)

class Cities(models.Model):
    Name = models.CharField(max_length=50)
    Province = models.ForeignKey(Provinces, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('Name', 'Province')

class MayorCities(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    City = models.ForeignKey(Cities, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('User', 'City')

class CityProblem(models.Model):
    problem_type = [
        ('Lighting', 'Lighting'),
        ('Garbage', 'Garbage'),
        ('Street', 'Street'),
        ('Other', 'Other'),
    ]

    City = models.ForeignKey(Cities, on_delete=models.CASCADE)
    Information = models.TextField()
    Reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    Type = models.CharField(choices=problem_type, max_length=20)
    Picture = models.ImageField(upload_to='CivicProblem_Pictures/', null=True, blank=True)
    Video = models.FileField(upload_to='CivicProblem_Videos', null=True, blank=True)
    DateTime = models.DateTimeField(auto_now_add=True)

class ReportCitizen(models.Model):
    Reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    Reported = models.ForeignKey(CityProblem, on_delete=models.CASCADE)
    Report = models.CharField(max_length=100)
    class Meta:
        unique_together = ('Reporter', 'Reported')

class CityProblemProsecute(models.Model):
    status_type = [
        ('examination', 'examination'),
        ('solved','solved'),
    ]

    CityProblem = models.ForeignKey(CityProblem, on_delete=models.CASCADE)
    Prosecuter = models.ForeignKey(User, on_delete=models.CASCADE)
    Status = models.CharField(choices=status_type, max_length=20)
    DateTime = models.DateTimeField(auto_now=True)

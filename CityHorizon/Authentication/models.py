from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    account_type = [
        ("Admin", "Admin"),
        ("Mayor", "Mayor"),
        ("Citizen", "Citizen"),
    ]

    account_theme = [
        ("Light", "Light"),
        ("dark", "dark"),
    ]

    FullName = models.CharField(max_length=255)
    Email = models.EmailField(unique=True)
    Password = models.CharField(max_length=255)
    Type = models.CharField(max_length=20, choices=account_type, blank=False, null=False, default="Citizen")
    LastCooperation = models.DateField(auto_now=False, auto_now_add=False, default=None, null=True, blank=True)
    Verified = models.BooleanField(default=False)
    Picture = models.ImageField(upload_to="Profile_Pictures", null=True, blank=True)
    Theme = models.CharField(max_length=10, choices=account_theme, null=True, default='Light')
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
    status_type = [
        ('PendingReview', 'PendingReview'),
        ('UnderConsideration','UnderConsideration'),
        ('IssueResolved','IssueResolved')
    ]

    City = models.ForeignKey(Cities, on_delete=models.CASCADE)
    Information = models.CharField(max_length=200)
    Reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    Type = models.CharField(choices=problem_type, max_length=20)
    Picture = models.ImageField(upload_to='CivicProblem_Pictures/', null=True, blank=True)
    Video = models.FileField(upload_to='CivicProblem_Videos', null=True, blank=True)
    DateTime = models.DateTimeField(auto_now_add=True)
    Longitude = models.FloatField()
    Latitude = models.FloatField()
    FullAdress = models.CharField(max_length=300)
    Status = models.CharField(default='PendingReview', choices=status_type, max_length=20)

class ReportCitizen(models.Model):
    Reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    Reported = models.ForeignKey(CityProblem, on_delete=models.CASCADE)
    Report = models.CharField(max_length=100)
    class Meta:
        unique_together = ('Reporter', 'Reported')

class CityProblemProsecute(models.Model):
    CityProblem = models.ForeignKey(CityProblem, on_delete=models.CASCADE)
    Prosecuter = models.ForeignKey(User, on_delete=models.CASCADE)

class MayorNote(models.Model):
    NoteOwner = models.ForeignKey(User, on_delete=models.CASCADE)
    Information = models.CharField(max_length=1000)
    CityProblem = models.ForeignKey(CityProblem, on_delete=models.CASCADE)

class Notification(models.Model):
    update_type  = [
        ('UnderConsideration', 'UnderConsideration'),
        ('IssueResolved', 'IssueResolved')
    ]
    Message = models.CharField(max_length=1000)
    Receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Receiver')
    CityProblem = models.ForeignKey(CityProblem, on_delete=models.CASCADE, related_name='CityProblem')
    UpdatedTo = models.CharField(max_length=30, choices=update_type)
    Date = models.DateTimeField(auto_now_add=True)
    Seen = models.BooleanField(default=False)
    Sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Sender')

class CityProblemReaction(models.Model):
    CityProblem = models.ForeignKey(CityProblem, on_delete=models.CASCADE, related_name='CivicProblem')
    Like = models.BooleanField()
    Reactor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Reactor')
    class Meta:
        unique_together = ('CityProblem', 'Reactor')

class MayorPriority(models.Model):
    priority_type = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    Mayor = models.ForeignKey(User, on_delete=models.CASCADE)
    CityProblem = models.ForeignKey(CityProblem, on_delete=models.CASCADE, related_name='CityProblemMayorPriority')
    Priority = models.CharField(max_length=20, choices=priority_type, default='Low')
    class Meta:
        unique_together = ('Mayor', 'Priority')
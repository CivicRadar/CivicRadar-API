from django.db import models
from Authentication.models import User


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

class CityReport(models.Model):
    City = models.ForeignKey(Cities, on_delete=models.CASCADE)
    Information = models.TextField()
    Reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    DateTime = models.DateTimeField(auto_now_add=True)

class CityReportProsecute(models.Model):
    status_type = [
        ('examination', 'examination'),
        ('solved','solved'),
    ]

    CityReport = models.ForeignKey(CityReport, on_delete=models.CASCADE)
    Prosecuter = models.ForeignKey(User, on_delete=models.CASCADE)
    Status = models.CharField(choices=status_type, max_length=20)
    DateTime = models.DateTimeField(auto_now=True)

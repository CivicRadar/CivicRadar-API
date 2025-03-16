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
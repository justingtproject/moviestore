from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

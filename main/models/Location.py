from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.sessions.models import Session

# Create your models here.
class Location(models.Model):
    user = models.ForeignKey( settings.AUTH_USER_MODEL, default=1, verbose_name="User", on_delete=models.SET_DEFAULT, )    
    session_key = models.CharField(max_length=300, blank=True, null=True)
    name = models.CharField(max_length=200)
    street_address_line1 = models.CharField(max_length=300)
    street_address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=4)
    zipcode = models.CharField(max_length=12)
    lat = models.DecimalField(max_digits=12, decimal_places=9)
    long = models.DecimalField(max_digits=12, decimal_places=9)
    
    def __str__(self):
        return self.name

from django.db import models
from datetime import datetime

# Create your models here.
class Location(models.Model):
    location_name = models.CharField(max_length=200)
    location_street_address_line1 = models.CharField(max_length=300)
    location_street_address_line2 = models.CharField(max_length=300)
    location_city = models.CharField(max_length=80)
    location_state = models.CharField(max_length=4)
    location_zipcode = models.CharField(max_length=12)
    location_lat = models.DecimalField(max_digits=12, decimal_places=9)
    location_long = models.DecimalField(max_digits=12, decimal_places=9)

    def __str__(self):
        return self.location_name


class Profile(models.Model):
    loc_hist_file = models.FileField(upload_to='loc_hist/')
    uploaded_at = models.DateTimeField(default=datetime.now, blank=True)
    
    def __str__(self):
        return self.loc_hist_file.name
        
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=50)
    formatted_name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    temp = models.IntegerField(null=True)
    pressure_mm = models.IntegerField(null=True)
    wind_speed = models.FloatField(null=True)
    upd_time = models.DateTimeField(null=True)

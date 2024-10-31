from django.db import models

# Create your models here.
from django.db import models

from devices.models import Device


class Data(models.Model):
    """
    Device Data manager.
    """
    api_key = models.CharField(max_length=34, help_text="Device API Key")
    pin = models.CharField(max_length=3, help_text="PIN value from V0 to V50")
    name = models.CharField(max_length=30, help_text="Device name")
    value = models.CharField(max_length=20, default='0', help_text="Value of the sensor") 
    date = models.DateTimeField('Publish Date', blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        """
        Return Device Name and Private Key
        """
        return "{}-{}".format(self.name, self.pk)
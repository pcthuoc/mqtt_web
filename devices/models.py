from django.db import models
from django.contrib.auth.models import User
from api_key.models import APIKey
from django.utils import timezone

class Device(models.Model):
    RELAY = 1
    SENSOR = 2
    VAN = 3
    DEVICE_TYPE_CHOICES = (
        (RELAY, 'Relay'),
        (SENSOR, 'Sensor'),
        (VAN, 'Van'),
    )

    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, blank=True, help_text="API_KEY")
    type = models.IntegerField(choices=DEVICE_TYPE_CHOICES, default=RELAY, help_text="Device type")
    name = models.CharField(max_length=30, help_text="Device name")
    pin = models.CharField(
        max_length=3, 
        choices=[(f'V{i}', f'V{i}') for i in range(51)], 
        help_text="PIN value from V0 to V50"
    )
    unit = models.CharField(max_length=20, blank=True, help_text="Unit of measurement")
    value = models.CharField(max_length=20, default='0', help_text="Value of the sensor")
    icon = models.CharField(max_length=100, blank=True, help_text="Icon name or identifier")
    last_on = models.DateTimeField('Time Last On', default=timezone.now)
    last_off = models.DateTimeField('Time Last Off', default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')

    pump_pin = models.CharField(max_length=3, default='V0', help_text="Pump PIN value from V0 to V50")
    mode = models.IntegerField(default=1, help_text="Mode")
    minute = models.IntegerField(default=0, help_text="Duration in minutes")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """
        Return Device Name and Private Key
        """
        return "{}-{}".format(self.name, self.pk)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

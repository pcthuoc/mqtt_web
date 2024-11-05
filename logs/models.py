from django.db import models
from django.utils import timezone
from api_key.models import APIKey


class APIStatus(models.Model):
    """
    Model to track the online status of an API.
    """
    api_key = models.OneToOneField(APIKey, on_delete=models.CASCADE, related_name='status')
    is_online = models.BooleanField(default=False, help_text="Current online status of the API")
    client_id = models.CharField(max_length=100, blank=True, help_text="Client ID of the device")
    username = models.CharField(max_length=100, blank=True, help_text="Username used by the client")
    keepalive = models.IntegerField(null=True, blank=True, help_text="Keepalive interval of the client in seconds")
    proto_ver = models.IntegerField(null=True, blank=True, help_text="MQTT protocol version used by the client")

    def __str__(self):
        return f"{self.api_key} - {'Online' if self.is_online else 'Offline'}"


class APILog(models.Model):
    """
    Model to store connection history and events for an API.
    """
    CONNECTED = 'client.connected'
    DISCONNECTED = 'client.disconnected'
    CONNACK = 'client.connack'

    EVENT_CHOICES = [
        (CONNECTED, 'Connected'),
        (DISCONNECTED, 'Disconnected'),
        (CONNACK, 'Connack'),
    ]

    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='logs')
    event = models.CharField(max_length=50, choices=EVENT_CHOICES, help_text="Event type")
    timestamp = models.DateTimeField(default=timezone.now, help_text="Time of the event")
    description = models.TextField(blank=True, help_text="Additional details about the event")
    client_id = models.CharField(max_length=100, blank=True, help_text="Client ID of the device")
    username = models.CharField(max_length=100, blank=True, help_text="Username used by the client")
    reason = models.CharField(max_length=100, blank=True, help_text="Reason for disconnection, if applicable")
    sockname = models.CharField(max_length=100, blank=True, help_text="Socket information of the broker")
    peername = models.CharField(max_length=100, blank=True, help_text="Socket information of the client")
    keepalive = models.IntegerField(null=True, blank=True, help_text="Keepalive interval of the client in seconds")
    proto_ver = models.IntegerField(null=True, blank=True, help_text="MQTT protocol version used by the client")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.api_key} - {self.get_event_display()} at {self.timestamp}"

from rest_framework import serializers
from devices.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'name', 'pin', 'value', 'type', 'unit', 'icon', 'last_on', 'last_off', 'pump_pin', 'mode', 'minute', 'created_at']

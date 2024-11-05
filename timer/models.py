from django.db import models
from django.core.cache import cache
from devices.models import Device
from multiselectfield import MultiSelectField

class Timer(models.Model):

    DAYS_OF_WEEK_CHOICES = [
        (0, 'Hai'),
        (1, 'Ba'),
        (2, 'Tư'),
        (3, 'Năm'),
        (4, 'Sáu'),
        (5, 'Bảy'),
        (6, 'Chủ Nhật'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='timers', help_text="Linked device for the timer")
    days_of_week = MultiSelectField(
        choices=DAYS_OF_WEEK_CHOICES,
        default=[0, 1, 2, 3, 4, 5, 6],
        max_choices=7,  
        max_length=13, 
        help_text="Days of the week when the event should trigger"
    )
    start_time = models.TimeField(help_text="Start time for the device to turn on (HH:MM)")
    end_time = models.TimeField(help_text="End time for the device to turn off (HH:MM)")
    is_active = models.BooleanField(default=True, help_text="Status to activate or deactivate the timer")
    
    def get_days_of_week_display(self):
        return ", ".join([dict(self.DAYS_OF_WEEK_CHOICES).get(day, '') for day in self.days_of_week if day is not None])
    
    class Meta:
        ordering = ['start_time']

    def __str__(self):
        day_names = [dict(self.DAYS_OF_WEEK_CHOICES).get(day, '') for day in self.days_of_week if day is not None]
        return f"Timer for {self.device.name} on {', '.join(day_names)} from {self.start_time} to {self.end_time}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete_pattern("active_timers_*")
        

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete_pattern("active_timers_*")

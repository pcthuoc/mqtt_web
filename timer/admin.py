from django.contrib import admin
from .models import Timer

@admin.register(Timer)
class TimerAdmin(admin.ModelAdmin):
    list_display = ('device', 'start_time', 'end_time', 'is_active', 'get_days_of_week')
    list_filter = ('is_active', 'days_of_week')
    search_fields = ('device__name',)
    ordering = ('start_time',)

    def get_days_of_week(self, obj):
        return ", ".join([dict(obj.DAYS_OF_WEEK_CHOICES).get(day, '') for day in obj.days_of_week if day is not None])
    get_days_of_week.short_description = "Days of Week"

    fieldsets = (
        (None, {
            'fields': ('device', 'days_of_week', 'start_time', 'end_time', 'is_active')
        }),
    )

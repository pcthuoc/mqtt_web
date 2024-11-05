from django.contrib import admin
from .models import APIStatus, APILog

@admin.register(APIStatus)
class APIStatusAdmin(admin.ModelAdmin):
    list_display = ('api_key', 'is_online', 'client_id', 'username', 'keepalive', 'proto_ver')
    list_filter = ('is_online', 'proto_ver')
    search_fields = ('api_key__key', 'client_id', 'username')
    ordering = ('-is_online',)
    readonly_fields = ('api_key', 'client_id', 'username', 'keepalive', 'proto_ver')

    def has_add_permission(self, request):
        # Không cho phép thêm trực tiếp APIStatus trong admin
        return False


@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ('api_key', 'event', 'timestamp', 'client_id', 'username', 'reason')
    list_filter = ('event', 'timestamp')
    search_fields = ('api_key__key', 'client_id', 'username')
    ordering = ('-timestamp',)
    readonly_fields = ('api_key', 'event', 'timestamp', 'client_id', 'username', 'reason', 'sockname', 'peername', 'keepalive', 'proto_ver', 'description')

    def has_add_permission(self, request):
        # Không cho phép thêm trực tiếp APILog trong admin
        return False

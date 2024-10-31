from django import forms
from django.contrib import admin
from .models import Device
from api_key.models import APIKey
from import_export.admin import ImportExportModelAdmin

class DeviceAdmin(ImportExportModelAdmin):
    """
    Custom admin for Device model.
    """
    list_display = ('name', 'api_key', 'get_device_type', 'pin', 'unit', 'value', 'created_at')
    search_fields = ['name', 'pin']
    list_filter = ['api_key', 'type']
    readonly_fields = ['created_at']
    
    # Ẩn trường api_key khi thêm mới thiết bị
    exclude = ['api_key']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'api_key':
            try:
                kwargs["queryset"] = APIKey.objects.all()
            except Exception as e:
                self.message_user(request, "Có lỗi khi truy xuất các khóa API. Vui lòng thử lại sau.", level='ERROR')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'pin':
            # Lấy ID của đối tượng hiện tại từ URL
            obj_id = request.resolver_match.kwargs.get('object_id')
            used_pins = Device.objects.exclude(pk=obj_id).values_list('pin', flat=True).distinct()
            current_pin = kwargs.get('initial', None)
            choices = [(f'V{i}', f'V{i}') for i in range(51) if f'V{i}' not in used_pins]
            if current_pin and current_pin not in [choice[0] for choice in choices]:
                choices.append((current_pin, current_pin))  # Thêm giá trị hiện tại vào danh sách lựa chọn
            kwargs['choices'] = choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_device_type(self, obj):
        return 'Relay' if obj.type == 1 else 'Sensor'

    get_device_type.short_description = 'Type'

admin.site.register(Device, DeviceAdmin)
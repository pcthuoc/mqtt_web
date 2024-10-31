# datas/admin.py

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Data
from .resources import DataResource

class DataAdmin(ImportExportModelAdmin):
    """
    Admin configuration for Data model with import/export functionality.
    """
    resource_class = DataResource
    list_display = (
        'pk', 'api_key', 'pin', 'name', 'value', 'date',)
    search_fields = ['api_key', 'pin', 'name']

admin.site.register(Data, DataAdmin)
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import UpdateDeviceValueByVPINAndAPIKey
urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('relays/', views.relays, name='relays'),
    path('device/update-value/<str:vpin>/<str:api_key>/', UpdateDeviceValueByVPINAndAPIKey.as_view(), name='update-device-value-by-vpin-and-apikey'),
    path('sensors/', views.sensors, name='sensors'),
    

    path('users/', views.listuser, name='users'),
    path('create_user/', views.create_user, name='create_user'),
    path('edit_user/', views.edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change_password/', views.change_password, name='change_password'),


    path('devices/', views.device_list, name='device_list'),  # Đường dẫn chính xác
    path('add_device/', views.add_device, name='device_add'),
    path('delete_device/<int:device_id>/', views.delete_device, name='device_delete'),
    path('get_device/<int:device_id>/', views.get_device, name='device_detail'),  # API lấy chi tiết thiết bị
    path('get_available_pins/<int:user_id>/', views.get_available_pins, name='get_available_pins'),
    path('edit_device/<int:device_id>/', views.edit_device, name='device_edit'),




]

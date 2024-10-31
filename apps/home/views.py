

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from datetime import timedelta
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

import datetime
import json
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse

from rest_framework.permissions import IsAuthenticated
from data.models import Data
from devices.models import Device
from api_key.models import APIKey
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .forms import SignUpForm
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import DeviceSerializer
from api_key.models import APIKey

logger = logging.getLogger(__name__)




class UpdateDeviceValueByVPINAndAPIKey(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, vpin, api_key):

        api_key_instance = get_object_or_404(APIKey, api_key=api_key)
        device = get_object_or_404(Device, pin=vpin, api_key=api_key_instance)
        new_value = request.data.get('value')

        if new_value is None:
            return Response({"error": "Giá trị 'value' là bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)

        if int(new_value) == 1:
            device.last_on = timezone.now()
            print(1)
        elif int(new_value )== 0:
            device.last_off = timezone.now()
            print(0)

        device.value = new_value
        device.save()
        serializer = DeviceSerializer(device)
        return Response(serializer.data, status=status.HTTP_200_OK)

def relays(request):
    relays = Device.objects.filter(type__in=[1, 3], user=request.user).order_by('type', '-id')
    try:
        api_key = APIKey.objects.get(user=request.user).api_key
    except APIKey.DoesNotExist:
        api_key = None 

    
    fake_relays = [{'name': f'Bơm {i}', 'pin': i} for i in range(1, 11)]

    context = {
        'segment': 'relay',
        'relays': relays,
        'fake_relays': fake_relays,
        'api_key': api_key
    }
    
  
    html_template = loader.get_template('home/relays.html')
    return HttpResponse(html_template.render(context, request))

def sensors(request):
    sensors = Device.objects.filter(type__in=[2], user=request.user).order_by('type', '-id')
    try:
        api_key = APIKey.objects.get(user=request.user).api_key
    except APIKey.DoesNotExist:
        api_key = None 


    context = {
        'segment': 'sensors',
        'sensors': sensors,
        'api_key': api_key
    }
    
  
    html_template = loader.get_template('home/sensors.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def listuser(request):
    users = User.objects.all()
    all_api_keys = APIKey.objects.all()
    form = SignUpForm() 
    context = {
        'segment': 'users',
        'users': users,
        'all_api_keys': all_api_keys,
        'form': form
    }

    return render(request, 'home/users.html', context)


@login_required(login_url="/login/")
def create_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return JsonResponse({'message': 'User created successfully.'}, status=201)
        return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'message': 'Invalid request.'}, status=405)
    
@csrf_exempt
def edit_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        email = request.POST.get('email')

        try:
            user = User.objects.get(id=user_id)
            user.username = username
            user.email = email
            user.save()
            return JsonResponse({'message': 'User updated successfully.'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)

    return JsonResponse({'error': 'Invalid request.'}, status=400)

@csrf_exempt
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({'message': 'User deleted successfully.'}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found.'}, status=404)
@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            return JsonResponse({'errors': {'password': ['Passwords do not match']}}, status=400)

        user = get_object_or_404(User, id=user_id)
        user.set_password(new_password)
        user.save()

        return JsonResponse({'message': 'Password changed successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)




def device_list(request):
    devices = Device.objects.all()
    api_keys = APIKey.objects.all()

    return render(request, 'home/devices.html', {
        'all_devices': devices,
        'all_api_keys': api_keys,
    })

def get_available_pins(request, user_id):
    """Trả về danh sách pin khả dụng cho một người dùng."""
    # Lấy danh sách pin đã sử dụng bởi người dùng
    used_pins = Device.objects.filter(user_id=user_id).values_list('pin', flat=True)
    all_pins = [f"V{i}" for i in range(51)]  # Pin từ V0 đến V50
    available_pins = [pin for pin in all_pins if pin not in used_pins]
    return JsonResponse(available_pins, safe=False)

def add_device(request):
    if request.method == 'POST':
        api_key_value = request.POST.get('api_key')
        user_id = request.POST.get('user')  # Sửa từ 'user_id' thành 'user' theo form
        device_name = request.POST.get('name')
        pin = request.POST.get('pin', 'V0')
        device_type = request.POST.get('type', 1)  # Kiểm tra kiểu dữ liệu nếu cần
        unit = request.POST.get('unit', '')
        value = request.POST.get('value', '0')

        # In ra giá trị để kiểm tra
        print(api_key_value)
        print(user_id)
        print(device_name)

        # Kiểm tra các trường bắt buộc
        if not api_key_value or not user_id or not device_name:
            return HttpResponseBadRequest("Thiếu API key, user ID hoặc tên thiết bị.")

        # Lấy APIKey và kiểm tra tính hợp lệ
        api_key = get_object_or_404(APIKey, api_key=api_key_value, user_id=user_id)

        # Tạo và lưu thiết bị mới
        device = Device(
            api_key=api_key,
            name=device_name,
            pin=pin,
            type=device_type,
            user=api_key.user,
            unit=unit,
            value=value
        )
        device.save()

        return JsonResponse({'message': 'Thiết bị đã được thêm thành công.'})

    return HttpResponseBadRequest("Yêu cầu không hợp lệ.")
def delete_device(request, device_id):
    if request.method == 'DELETE':
        device = get_object_or_404(Device, id=device_id)
        device.delete()
        return JsonResponse({'message': 'Device deleted successfully'}, status=200)

def get_device(request, device_id):
    print(f"Lấy thông tin thiết bị với ID: {device_id}")

    device = get_object_or_404(Device, id=device_id)

    # Tạo dictionary chứa dữ liệu trả về
    data = {
        'id': device.id,
        'name': device.name,
        'type': device.type,
        'pin': device.pin,
        'unit': device.unit,
        'api_key': device.api_key.api_key,  # Trả về API key
        'user_id': device.api_key.user.id   # Trả về ID của người dùng liên kết
    }

    # Trả về dữ liệu dưới dạng JSON
    return JsonResponse(data)
def get_available_pins_view(request, user_id):
    print(user_id)
    pins = get_available_pins(user_id)
    return JsonResponse(list(pins), safe=False)  
# Chỉnh sửa thông tin thiết bị
@csrf_exempt  # Tắt kiểm tra CSRF cho thử nghiệm, bạn có thể bỏ khi không cần
def edit_device(request, device_id):
    if request.method == 'POST':
        try:
            device = get_object_or_404(Device, id=device_id)

            # Lấy dữ liệu từ form
            name = request.POST.get('name')
            pin = request.POST.get('pin')
            unit = request.POST.get('unit')

            # Cập nhật dữ liệu cho thiết bị
            device.name = name
            device.pin = pin
            device.unit = unit
            device.save()

            return JsonResponse({'message': 'Thiết bị đã được cập nhật thành công.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Yêu cầu không hợp lệ.'}, status=400)  
@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

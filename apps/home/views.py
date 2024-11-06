

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
import paho.mqtt.client as mqt
import datetime
import json
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from data.models import Data
from devices.models import Device
from api_key.models import APIKey
from timer.models import Timer
from django.core.cache import cache
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .forms import SignUpForm,TimerForm
from django.views.decorators.http import require_POST

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import DeviceSerializer
from api_key.models import APIKey
from logs.models import APIStatus, APILog
from mqtt.mqtt_client import publish_message
from django.views.decorators.http import require_http_methods
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
          
        elif int(new_value) == 0:
            device.last_off = timezone.now()
       

    
        device.value = new_value
        topic = f"API/{api_key}/{vpin}/"
            # Tạo payload cơ bản
        payload = {
                'value': new_value,
                'event_type': 'server_update'
        }
        publish_message(topic, payload)
        device.save()
        serializer = DeviceSerializer(device)
        return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
def mqtt_authorization(request):
    if request.method in ["POST", "GET"]:
        try:
            # Parse dữ liệu từ request
            data = json.loads(request.body.decode("utf-8"))
            username = data.get("username")
            topic = data.get("topic")
            action = data.get("action")
  

            # Kiểm tra username và password trong settings
            if username == settings.MQTT_USERNAME:
             
                return JsonResponse({"result": "allow"}, status=200)

            # Nếu không khớp với settings, kiểm tra dựa trên API key và các điều kiện khác
            if action in ["publish", "subscribe"] and username in topic:
                # Kiểm tra nếu API key tồn tại cho username này
                if APIKey.objects.filter(api_key=username).exists():
              
                    return JsonResponse({"result": "allow"}, status=200)
                else:
           
                    return JsonResponse({"result": "deny"}, status=200)
            else:

                return JsonResponse({"result": "deny"}, status=200)

        except json.JSONDecodeError:
            # Lỗi khi JSON không hợp lệ
            return JsonResponse({"result": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:

            return JsonResponse({"result": "error", "message": str(e)}, status=400)
    else:
        # Trả về lỗi nếu phương thức không phải là POST hoặc GET
        return JsonResponse({"result": "method_not_allowed"}, status=405)
@csrf_exempt
def mqtt_auth(request):
    if request.method in ["POST", "GET"]:
        try:
            # Lấy dữ liệu từ request body và chuyển đổi thành dictionary
            data = json.loads(request.body.decode("utf-8"))
            username = data.get("username")
            password = data.get("password")
            topic = data.get("topic")
            # Kiểm tra username và password với các giá trị trong settings
            if username == settings.MQTT_USERNAME and password == settings.MQTT_PASSWORD:
                return JsonResponse({"result": "allow"}, status=200)
            else:
                # Nếu không khớp, tiến hành kiểm tra API key như cũ
                if APIKey.objects.filter(api_key=username).exists():
                    # Kiểm tra thêm quyền truy cập vào topic nếu cần

                    return JsonResponse({"result": "allow"}, status=200)
                else:
                    return JsonResponse({"result": "deny"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"result": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"result": "error", "message": str(e)}, status=400)
    else:
        return JsonResponse({"result": "method_not_allowed"}, status=405)

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

    api_status = APIStatus.objects.filter(api_key__user=request.user).first()
    api_log_list = APILog.objects.filter(api_key__user=request.user).order_by('-timestamp')[:10] if api_status else []
   
    context = {
        'segment': 'index',
        'api_status': api_status,
        'api_log_list': api_log_list,
    }
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))
def timer(request):
    relay_devices = Device.objects.filter(user=request.user, type=1)
    timers = Timer.objects.filter(device__in=relay_devices).select_related('device').order_by('device__pin')

    context = {
        'segment': 'timer',
        'timers': timers,
        'relay_devices': relay_devices,
    }

    html_template = loader.get_template('home/timer.html')
    return HttpResponse(html_template.render(context, request))
@require_http_methods(["GET", "POST"])
def add_edit_timer(request, timer_id=None):
    # Kiểm tra xem đang ở chế độ thêm mới hay chỉnh sửa
    timer = get_object_or_404(Timer, id=timer_id, device__user=request.user) if timer_id else None

    if request.method == 'POST':


        form = TimerForm(request.POST, instance=timer)
        if form.is_valid():
            timer = form.save(commit=False)
            timer.device.user = request.user  # Đảm bảo Timer thuộc về user hiện tại


            timer.save()
            timer_data = {
                'id': timer.id,
                'device_name': timer.device.name,
                'start_time': timer.start_time.strftime('%H:%M'),
                'end_time': timer.end_time.strftime('%H:%M'),
                'days_of_week': timer.get_days_of_week_display(),
                'is_active': timer.is_active,
            }

            return JsonResponse({'message': 'Timer đã được lưu thành công.', 'timer': timer_data}, status=200)
        else:

            return JsonResponse({'errors': form.errors}, status=400)
    
    # GET request: Trả về thông tin Timer cho AJAX trong trường hợp chỉnh sửa
    if timer:
        data = {
            'id': timer.id,
            'device': timer.device.id,
            'days_of_week': timer.days_of_week,
            'start_time': timer.start_time.strftime('%H:%M'),
            'end_time': timer.end_time.strftime('%H:%M'),
            'is_active': timer.is_active,
        }
 
        return JsonResponse(data, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def delete_timer(request, timer_id):
    timer = get_object_or_404(Timer, id=timer_id, device__user=request.user)
    timer.delete()
    return JsonResponse({'message': 'Timer đã được xóa thành công.', 'timer_id': timer_id}, status=200)

def add_timer(request):
    if request.method == 'POST':
        form = TimerForm(request.POST)
        if form.is_valid():
            timer = form.save(commit=False)
            timer.device.user = request.user  # Đảm bảo Timer thuộc về user hiện tại
            timer.save()
            # Chuẩn bị dữ liệu JSON để trả về
            timer_data = {
                'id': timer.id,
                'device_name': timer.device.name,
                'start_time': timer.start_time.strftime('%H:%M'),
                'end_time': timer.end_time.strftime('%H:%M'),
                'days_of_week': timer.get_days_of_week_display(),
                'is_active': timer.is_active,
            }
            return JsonResponse({'message': 'Timer đã được thêm thành công.', 'timer': timer_data}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    
    # Nếu không phải POST, trả về lỗi
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@require_POST
def toggle_timer_status(request):
    timer_id = request.POST.get('timer_id')
    is_active = request.POST.get('is_active') == 'true'  # Chuyển chuỗi thành boolean

    timer = get_object_or_404(Timer, id=timer_id, device__user=request.user)
    timer.is_active = is_active
    timer.save()

    return JsonResponse({'message': 'Trạng thái của Timer đã được cập nhật.'})


def chart_view(request):
    now = datetime.datetime.now()

    # Mặc định lấy dữ liệu cho 7 ngày của mỗi biểu đồ khi trang được tải lần đầu
    default_days = 7
    start_date = now - datetime.timedelta(days=default_days)

    # Lấy APIKey đối tượng của người dùng hiện tại
    api_key_obj = get_object_or_404(APIKey, user=request.user)

    # Lấy dữ liệu mặc định cho 7 ngày của mỗi pin V0, V1, V2, V3
    data_v0 = Data.objects.filter(api_key=api_key_obj.api_key, pin='V0', date__gte=start_date).values('value', 'date')
    data_v1 = Data.objects.filter(api_key=api_key_obj.api_key, pin='V1', date__gte=start_date).values('value', 'date')
    data_v2 = Data.objects.filter(api_key=api_key_obj.api_key, pin='V2', date__gte=start_date).values('value', 'date')
    data_v3 = Data.objects.filter(api_key=api_key_obj.api_key, pin='V3', date__gte=start_date).values('value', 'date')

    # Lấy các đối tượng Device tương ứng với các pin V0 đến V3
    sensor0 = Device.objects.filter(api_key=api_key_obj, pin='V0').first()
    sensor1 = Device.objects.filter(api_key=api_key_obj, pin='V1').first()
    sensor2 = Device.objects.filter(api_key=api_key_obj, pin='V2').first()
    sensor3 = Device.objects.filter(api_key=api_key_obj, pin='V3').first()

    # Hàm chuyển đổi dữ liệu thành định dạng JSON
    def serialize_data(data):
        return [{'value': item['value'], 'date': item['date'].isoformat()} for item in data]

    # Serialize dữ liệu
    data_list_v0 = serialize_data(data_v0)
    data_list_v1 = serialize_data(data_v1)
    data_list_v2 = serialize_data(data_v2)
    data_list_v3 = serialize_data(data_v3)

    context = {
        'segment': 'chart',
        'data_list_v0': json.dumps(data_list_v0),
        'data_list_v1': json.dumps(data_list_v1),
        'data_list_v2': json.dumps(data_list_v2),
        'data_list_v3': json.dumps(data_list_v3),
        'sensor0': sensor0,
        'sensor1': sensor1,
        'sensor2': sensor2,
        'sensor3': sensor3,
    }

    html_template = loader.get_template('home/chart.html')
    return HttpResponse(html_template.render(context, request))   
def get_data_by_timeframe_and_pin(request, timeframe, pin):
    # Xác định thời gian hiện tại và thời gian bắt đầu dựa trên `timeframe`
    api_key = get_object_or_404(APIKey, user=request.user).api_key
    end_time = timezone.now()
    if timeframe == '1h':
        start_time = end_time - timedelta(hours=1)
    elif timeframe == '6h':
        start_time = end_time - timedelta(hours=6)
    elif timeframe == '12h':
        start_time = end_time - timedelta(hours=12)
    elif timeframe == '1d':
        start_time = end_time - timedelta(days=1)
    elif timeframe == '7d':
        start_time = end_time - timedelta(days=7)
    elif timeframe == '14d':
        start_time = end_time - timedelta(days=14)
    elif timeframe == '30d':
        start_time = end_time - timedelta(days=30)
    else:
        return JsonResponse({"error": "Invalid timeframe"}, status=400)

    # Lọc dữ liệu chỉ dựa trên `pin` và khoảng thời gian
    data_points = Data.objects.filter(api_key=api_key,pin=pin, date__range=(start_time, end_time)).order_by('date')

    # Chuyển đổi dữ liệu thành JSON
    chart_data = {
        'dates': [data.date.strftime('%Y-%m-%d %H:%M:%S') for data in data_points],
        'values': [float(data.value) for data in data_points]  
    }

    return JsonResponse(chart_data)
@csrf_exempt
def checking(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
 
            event_type = data.get('event')
            client_id = data.get('clientid')
            username = data.get('username')
            keepalive = data.get('keepalive')
            proto_ver = data.get('proto_ver')
            sockname = data.get('sockname')
            peername = data.get('peername')
            reason = data.get('reason', '')  
            

          
            try:
      
                api_key = APIKey.objects.get(api_key=username)  # Sửa lại để dùng api_key
        
            except APIKey.DoesNotExist:
    
                return JsonResponse({"status": "error", "message": "API Key not found"}, status=404)

           
            if event_type == 'client.connected':
          
             
                APIStatus.objects.update_or_create(
                    api_key=api_key,
                    defaults={
                        "is_online": True,
                        "client_id": client_id,
                        "username": username,
                        "keepalive": keepalive,
                        "proto_ver": proto_ver,
                    }
                )
              
                APILog.objects.create(
                    api_key=api_key,
                    event=event_type,
                    client_id=client_id,
                    username=username,
                    keepalive=keepalive,
                    proto_ver=proto_ver,
                    sockname=sockname,
                    peername=peername,
                )
       

            elif event_type == 'client.disconnected':

         
                APIStatus.objects.filter(api_key=api_key).update(is_online=False)
              
                APILog.objects.create(
                    api_key=api_key,
                    event=event_type,
                    client_id=client_id,
                    username=username,
                    reason=reason,
                    sockname=sockname,
                    peername=peername,
                )
         

            elif event_type == 'client.connack':
                APIStatus.objects.update_or_create(
                    api_key=api_key,
                    defaults={
                        "is_online": True,
                        "client_id": client_id,
                        "username": username,
                        "keepalive": keepalive,
                        "proto_ver": proto_ver,
                    }
                )
              
                APILog.objects.create(
                    api_key=api_key,
                    event=event_type,
                    client_id=client_id,
                    username=username,
                    keepalive=keepalive,
                    proto_ver=proto_ver,
                    sockname=sockname,
                    peername=peername,
                )


            return JsonResponse({"status": "success"}, status=200)
        
        except json.JSONDecodeError:
        
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    else:
      
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

def infor(request):
    # Lấy API key của người dùng hiện tại
    api_key = get_object_or_404(APIKey, user=request.user).api_key
    user = request.user
    # Lọc thiết bị theo user hiện tại
    devices = Device.objects.filter(user=user)
    # Lấy danh sách các PIN đang được sử dụng
    context = {
        'segment': 'infor',
        'api_key': api_key,
        'devices': devices,
    }

    return render(request, 'home/infor.html', context)
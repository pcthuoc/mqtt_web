import requests
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Q
from .models import Timer
from mqtt.mqtt_client import publish_message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
def notify_user(user_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_data_update",
            "data": data,
        }
    )


@shared_task
def check_and_update_timers():
    now = timezone.localtime()  # Lấy giờ địa phương
    current_day = now.weekday()  # Thứ hiện tại (0: Thứ Hai, ..., 6: Chủ Nhật)
    current_time = now.time().replace(second=0, microsecond=0)  # Chỉ lấy giờ và phút, bỏ giây và microsecond
    print(f"Giờ địa phương hiện tại: {current_time}")
    
    # Dùng cache để lưu bộ lọc Timer
    cache_key = f"active_timers_{current_day}_{current_time.minute}"
    active_timers = cache.get(cache_key)
    
    if active_timers is None:
        print("Không có cache, truy vấn cơ sở dữ liệu")
        # Truy vấn Timer có `start_time` hoặc `end_time` trùng với `current_time`
        active_timers = Timer.objects.filter(
            is_active=True,
        ).filter(
            Q(start_time=current_time) | Q(end_time=current_time)  # Lọc khi thời gian hiện tại trùng với start_time hoặc end_time
        )
        # Lưu kết quả vào cache mà không có thời gian hết hạn
        cache.set(cache_key, active_timers, timeout=None)
    
    for timer in active_timers:
        # Kiểm tra nếu thứ hiện tại có trong `days_of_week` của Timer
        if str(current_day) in timer.days_of_week:
            print("Thông tin Timer khớp với ngày và giờ hiện tại:")
            
            # Xác định trạng thái bật/tắt dựa trên thời gian
            if timer.start_time == current_time:
                timer.device.value = "1"  # Bật thiết bị
                action = "1"
                print("bât")
            elif timer.end_time == current_time:
                timer.device.value = "0"  # Tắt thiết bị
                action = "0"
                print("tắt")
            else:
                continue  # Nếu không trùng start_time hoặc end_time, bỏ qua timer này
            timer.device.save()
            # Gửi request tới endpoint cập nhật giá trị thiết bị
            device = timer.device
            api_key = device.api_key.api_key if hasattr(device, 'api_key') else None
            pin = device.pin
            topic = f"API/{api_key}/{pin}/"
                # Tạo payload cơ bản
            payload = {
                    'value': action,
                    'event_type': 'server_update'
            }     
            publish_message(topic, payload) 
            notify_user(device.user.id, {
                "id": device.id,
                "new_value": action,
                "last_off": timezone.localtime(device.last_off).strftime("%H:%M %d/%m/%Y") if device.last_off else None,
                "last_on": timezone.localtime(device.last_on).strftime("%H:%M %d/%m/%Y") if device.last_on else None
            }) 
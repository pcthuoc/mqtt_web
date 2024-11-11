import paho.mqtt.client as mqtt
import json
import logging
import threading
import queue
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

logger = logging.getLogger(__name__)
message_queue = queue.Queue()  # Hàng đợi để lưu trữ tin nhắn

# Cấu hình broker và thông tin đăng nhập
MQTT_BROKER_HOST = '165.232.166.11'
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = 'API/#'
MQTT_USERNAME = 'pcthuochh'
MQTT_PASSWORD = 'thuocadmin'
# Hàng đợi lưu trữ tin nhắn
message_queue = queue.Queue()
# Hàm gửi thông báo tới client qua WebSocket
def notify_user(user_id, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_data_update",
            "data": data,
        }
    )

# Hàm được gọi khi client kết nối thành công tới broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {settings.MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

# Hàm xử lý khi nhận được tin nhắn, đẩy tin nhắn vào hàng đợi
def on_message(client, userdata, msg):
    message = {
        'topic': msg.topic,
        'payload': msg.payload.decode("utf-8"),  # Giải mã ngay tại đây
        'timestamp': timezone.now()
    }

 
    message_queue.put(message)  # Đẩy tin nhắn vào hàng đợi
def publish_message(topic, payload):
    """
    Publish một tin nhắn lên MQTT broker.
    """
    try:
        client = mqtt.Client()
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
        
        # Publish tin nhắn lên topic
        client.publish(topic, json.dumps(payload))
        logger.info(f"Published to topic '{topic}' with payload '{payload}'")
        
        # Ngắt kết nối sau khi gửi tin nhắn
        client.disconnect()
        
    except Exception as e:
        logger.error(f"Failed to publish message: {e}")

def process_message_queue():
    while True:
        try:
            msg = message_queue.get()
            payload = msg.get("payload", "")
            data = json.loads(payload)
            topic_parts = msg.get("topic", "").split('/')

            if len(topic_parts) >= 4:
                api_key = topic_parts[1]
                topic_type = topic_parts[2]
                if topic_type.startswith("V"):
                    pin = topic_type
                    value = data.get("value")
                    event_type = data.get("event_type")
                    
                    if event_type == "client_update":
                        try:
                            # Import models bên trong block xử lý
                            from devices.models import Device
                            from data.models import Data
                            
                          
                            current_time_utc = timezone.now()  
                            device = Device.objects.filter(api_key__api_key=str(api_key), pin=str(pin)).first()

                            if device:
                                # Cập nhật giá trị thiết bị
                                device.value = value

                               
                                if device.type in [1, 3]:  
                                    if value == "0":
                                        device.last_off = current_time_utc
                                    else:
                                        device.last_on = current_time_utc
                                else:
                                  #  last_update = Data.objects.filter(api_key=api_key, pin=pin).order_by('-date').first()
                                   
                                    # if not last_update or (current_time_utc - last_update.date).total_seconds() >= 60:
                                    Data.objects.create(api_key=api_key, pin=pin, name=device.name, value=device.value, date=current_time_utc)
                                    device.last_off = current_time_utc

                                device.save()

                                # Chuyển đổi `last_on` và `last_off` về múi giờ địa phương khi gửi thông báo
                                notify_user(device.user.id, {
                                    "id": device.id,
                                    "new_value": value,
                                    "last_off": timezone.localtime(device.last_off).strftime("%H:%M %d/%m/%Y") if device.last_off else None,
                                    "last_on": timezone.localtime(device.last_on).strftime("%H:%M %d/%m/%Y") if device.last_on else None
                                })
                            else:
                                logger.warning(f"No device found with API: {api_key} and Pin: {pin} at topic: {msg.get('topic')}")

                        except Exception as e:
                            logger.error(f"[ERROR] An error occurred while handling the message: {e}")
                else:
                    logger.warning(f"Unhandled topic format: {msg.get('topic')}")
            else:
                logger.warning(f"Invalid topic format: {msg.get('topic')}")

            message_queue.task_done()

        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] JSON decoding failed: {e}")
            message_queue.task_done()
        except Exception as e:
            logger.error(f"[ERROR] Error processing message from queue: {e}")
            message_queue.task_done()
# Khởi tạo client MQTT và luồng xử lý hàng đợi
def start_mqtt_client():
    client = mqtt.Client()
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
    # Bắt đầu luồng xử lý hàng đợi
    threading.Thread(target=process_message_queue, daemon=True).start()

    # Vòng lặp client
    client.loop_forever()

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

# Callback khi kết nối thành công tới MQTT broker
def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected to MQTT broker with result code {rc}")
    if rc == 0:
        client.subscribe(settings.MQTT_TOPIC)
    else:
        logger.error(f"Connect failed with result code {rc}")

# Callback khi nhận tin nhắn MQTT
def on_message(client, userdata, msg):
    try:
        message_queue.put(msg)  # Đưa tin nhắn vào hàng đợi
    except Exception as e:
        logger.error(f"[ERROR] Error putting message in queue: {e}")

# Xử lý tin nhắn trong hàng đợi
def process_message_queue():
    while True:
        try:
            msg = message_queue.get()
            payload = msg.payload.decode("utf-8")
            data = json.loads(payload)
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 4:
                api_key = topic_parts[1]
                topic_type = topic_parts[2]
                if topic_type.startswith("V"):
                    pin = topic_type
                    value = data.get("value")
                    event_type = data.get("event_type")
                    if event_type == "update":
                        try:
                            from devices.models import Device
                            from data.models import Data
                            # Lấy thời gian hiện tại theo UTC và chuyển sang múi giờ cục bộ
                            current_time = timezone.localtime(timezone.now())
                        

                            device = Device.objects.filter(api_key__api_key=api_key, pin=pin).first()

                            if device:
                                # Cập nhật thiết bị và gửi giá trị mới tới client
                                device.value = value
                                print(device.pin)
                                now = timezone.localtime(timezone.now())  # Lấy thời gian với múi giờ cục bộ
                                
                                if device.type in [1, 3]:  # Relay hoặc Van
                                    if value == "0":
                                        device.last_off = now
                                    else:
                                        device.last_on = now
                                else:
                                    last_update = Data.objects.filter(api_key=api_key, pin=pin).order_by('-date').first()
                                    if not last_update or (current_time - last_update.date).total_seconds() >= 60:
                                        Data.objects.create(api_key=api_key, pin=pin, name=device.name, value=device.value, date=now)
                                    device.last_off = now

                                device.save()

                                # Gửi dữ liệu thay đổi tới người dùng
                                notify_user(device.user.id, {
                                    "sensor_id": device.id,
                                    "new_value": value,
                                    "last_off": device.last_off.strftime("%H:%M %d/%m/%Y") if device.last_off else None,
                                    "last_on": device.last_on.strftime("%H:%M %d/%m/%Y") if device.last_on else None
                                })
                            else:
                                logger.warning(f"No device found with API: {api_key} and Pin: {pin} at topic: {msg.topic}")
                        except Exception as e:
                            logger.error(f"[ERROR] An error occurred while handling the message: {e}")
                else:
                    logger.warning(f"Unhandled topic format: {msg.topic}")
            else:
                logger.warning(f"Invalid topic format: {msg.topic}")
            message_queue.task_done()
        except Exception as e:
            logger.error(f"[ERROR] Error processing message from queue: {e}")

# Hàm kết nối MQTT và lắng nghe
def connect_mqtt():
    client = mqtt.Client()
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
        logger.info("MQTT client connected")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        return None

def start_mqtt_client():
    client = connect_mqtt()
    if client:
        client.loop_forever()
        processing_thread = threading.Thread(target=process_message_queue)
        processing_thread.daemon = True
        processing_thread.start()
    else:
        logger.error("MQTT client failed to start")

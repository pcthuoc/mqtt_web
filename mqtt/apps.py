from django.apps import AppConfig
import threading
from .mqtt_client import start_mqtt_client

class MqttConfig(AppConfig):
    name = 'mqtt'

    def ready(self):
        mqtt_thread = threading.Thread(target=start_mqtt_client)
        mqtt_thread.daemon = True  # Đảm bảo dừng khi Django dừng
        mqtt_thread.start()

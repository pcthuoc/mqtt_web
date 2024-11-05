from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Thiết lập biến môi trường cho Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Tạo một instance của Celery
app = Celery('core')

# Nạp cấu hình từ settings.py với prefix 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tự động tìm và nạp các tác vụ (tasks) từ các app đã cài đặt
app.autodiscover_tasks()
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from .models import APIKey
import requests
from requests.auth import HTTPBasicAuth

# Cấu hình logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_api_key(sender, instance, created, **kwargs):
    if created:
        try:
            # Tạo API Key cho người dùng mới
            api_key_instance = APIKey.objects.create(user=instance)
            api_key = api_key_instance.api_key
            print(api_key)
            # Đặt tên topic gốc cho người dùng
            user_topic = f"API/{api_key}/#"
            # Gọi API EMQX để cấp quyền cho API Key trên topic
            url = "http://165.232.166.11:8081/api/v4/acl"
            headers = {"Content-Type": "application/json"}
            payload = {
                "username": api_key,      # Dùng API Key làm username
                "topic": user_topic,      # Topic cho phép với tất cả các sub-topics
                "action": "pubsub"        # Quyền truy cập: publish & subscribe
            }
            
            # # Gửi yêu cầu tạo ACL cho API Key trên EMQX
            # response = requests.post(
            #     url,
            #     json=payload,
            #     headers=headers,
            #     auth=HTTPBasicAuth(settings.EMQX_API_KEY, settings.EMQX_SECRET_KEY)
            # )

            # if response.status_code == 200:
            #     logger.info(f"Successfully created API Key and assigned topic for user {instance.username}")
            # else:
            #     logger.error(f"Failed to create ACL for API Key {api_key}: {response.content}")
                
        except Exception as e:
            logger.error(f"Error creating API Key or setting topic permissions: {str(e)}")

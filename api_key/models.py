# apikey/models.py

from django.db import models
from django.contrib.auth.models import User
import random
import string

def generate_api_key(length=32):
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class APIKey(models.Model):
    """
    Model for storing API keys.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=90, unique=True, help_text="Global API key", default=generate_api_key)

    def __str__(self):
        return self.api_key
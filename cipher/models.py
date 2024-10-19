from django.db import models
from django.contrib.auth.models import User
import uuid

class Text(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)  # Добавляем поле для названия
    content = models.TextField()
    original_content = models.TextField(blank=True, null=True)  # Добавляем поле для исходного текста
    key = models.CharField(max_length=200, blank=True, null=True)  # Добавляем поле для ключа
    is_encrypted = models.BooleanField(default=False)  # Флаг, указывающий, зашифрован ли текст
    is_manually_added = models.BooleanField(default=True)  # Новое поле
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RequestHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

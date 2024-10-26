from django.db import models
from django.contrib.auth.models import User
import uuid

class Text(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)  
    content = models.TextField()
    original_content = models.TextField(blank=True, null=True) 
    key = models.CharField(max_length=200, blank=True, null=True)  
    is_encrypted = models.BooleanField(default=False) 
    is_manually_added = models.BooleanField(default=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RequestHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

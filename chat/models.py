from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, db_index=True)
    content = models.TextField()
    tokens_used = models.IntegerField(default=0)
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)

    def __str__(self):
        return self.content[:30]


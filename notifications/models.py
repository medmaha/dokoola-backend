from django.db import models

from users.models import User

from utilities.generator import hex_generator


class Notification(models.Model):
    id = models.CharField(max_length=100, blank=True, primary_key=True, default=hex_generator)

    sender = models.ForeignKey(User, related_name='notification_sender', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='notification_recipient', on_delete=models.CASCADE)
    
    hint_text = models.CharField(max_length=300, default='')
    content_text = models.CharField(max_length=1000, default='')

    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(default='PROPOSAL', max_length=60)
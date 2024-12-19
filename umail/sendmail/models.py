import django.contrib
from django.contrib.auth.models import User
from django.db import models
import uuid


class EmailStatus(models.TextChoices):
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    OPENED = "opened", "Opened"
    PENDING="pending","Pending"

class Email_log(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name='sent_emails')
    recipient_email=models.EmailField()
    status=models.CharField(
        max_length=10,
        choices=EmailStatus.choices,
        default=EmailStatus.SENT,
    )
    is_scheduled=models.BooleanField(default=False)
    scheduled_time=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str_(self):
        return f"Email to {self.recipient_email}"

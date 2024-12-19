from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from .models import Email_log,EmailStatus


@shared_task
def add(x, y):
    return x + y

@shared_task
def send_email_task(email_id,message_content,):
    try:
        email_log=Email_log.objects.get(id=email_id)
        send_mail(
            subject="Important Notification",
            message=message_content,
            from_email="yadavadarshgamer@gmail.com",
            recipient_list=[email_log.recipient_email],
            fail_silently=False,
        )
        email_log.status=EmailStatus.SENT
        email_log.save()
    except Exception as e:
        email_log.status=EmailStatus.FAILED
        email_log.save()
        raise e


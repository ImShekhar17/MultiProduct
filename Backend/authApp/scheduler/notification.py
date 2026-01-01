from celery import shared_task
from authApp.models import Notification, User


@shared_task
def send_notification(receiver_id, title, message):
    
    try:
        receiver = User.objects.get(id=receiver_id)
        notification = Notification.objects.create(
            receiver=receiver,
            title=title,
            message=message
        )
        notification.save()
        return True
    except User.DoesNotExist:
        return False
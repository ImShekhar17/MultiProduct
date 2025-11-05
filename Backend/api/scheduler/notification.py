from celery import shared_task

@shared_task
def send_notification(receiver_id, title, message):
    from Backend.api.models import Notification, User
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
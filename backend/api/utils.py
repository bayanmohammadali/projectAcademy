from users.models import Notification

def send_notification(user, type, message):
    Notification.objects.create(
        user=user,
        type=type,
        message=message
    )
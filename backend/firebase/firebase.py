import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from users.models import FCMToken

# تهيئة Firebase مرة واحدة فقط
cred = credentials.Certificate("backend/firebase/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

def send_push_notification(user, title, body, data=None):
    tokens = FCMToken.objects.filter(user=user).values_list("token", flat=True)

    if not tokens:
        return  # ما في أجهزة مسجلة

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        tokens=list(tokens),
    )

    response = messaging.send_each_for_multicast(message)
    print(f"Sent: {response.success_count}, Failed: {response.failure_count}")

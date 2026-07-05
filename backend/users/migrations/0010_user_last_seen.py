from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_notification_related_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_seen',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

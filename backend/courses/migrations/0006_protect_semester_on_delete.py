from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_courseoffering_is_active'),
        ('academic', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseoffering',
            name='semester',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='course_offerings',
                to='academic.semester',
            ),
        ),
    ]

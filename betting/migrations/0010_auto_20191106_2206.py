# Generated by Django 2.2.6 on 2019-11-06 22:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0009_auto_20191106_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='punter',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

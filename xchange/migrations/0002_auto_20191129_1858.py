# Generated by Django 2.2.6 on 2019-11-29 18:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xchange', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

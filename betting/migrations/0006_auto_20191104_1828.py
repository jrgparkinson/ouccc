# Generated by Django 2.2.6 on 2019-11-04 18:28

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False


    dependencies = [
        ('betting', '0005_auto_20191102_2111'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Event',
            new_name='Competition',
        ),
        migrations.RenameModel(
            old_name='Runner',
            new_name='Competitor',
        ),
    ]
# Generated by Django 2.2.6 on 2019-11-07 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0011_auto_20191107_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='name',
            field=models.CharField(default='Varsity XC', max_length=200),
            preserve_default=False,
        ),
    ]

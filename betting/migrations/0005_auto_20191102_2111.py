# Generated by Django 2.2.6 on 2019-11-02 21:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0004_auto_20191102_2108'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='optionplacing',
            name='option_ptr',
        ),
        migrations.RemoveField(
            model_name='optionplacing',
            name='runner',
        ),
        migrations.RemoveField(
            model_name='optionteamscore',
            name='option_ptr',
        ),
        migrations.RemoveField(
            model_name='optionteamscore',
            name='team',
        ),
        migrations.RemoveField(
            model_name='optiontime',
            name='option_ptr',
        ),
        migrations.RemoveField(
            model_name='optiontime',
            name='runner',
        ),
        migrations.DeleteModel(
            name='Option',
        ),
        migrations.DeleteModel(
            name='OptionPlacing',
        ),
        migrations.DeleteModel(
            name='OptionTeamScore',
        ),
        migrations.DeleteModel(
            name='OptionTime',
        ),
    ]

# Generated by Django 3.0.2 on 2020-02-21 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osmcal', '0016_auto_20200221_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventparticipation',
            name='answers',
        ),
    ]

# Generated by Django 3.1.1 on 2020-09-28 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osmcal', '0025_auto_20200917_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='timezone',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

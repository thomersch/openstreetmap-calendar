# Generated by Django 3.0.3 on 2020-02-23 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osmcal', '0020_eventparticipation_added_on'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='participationquestion',
            options={'ordering': ('event', 'id')},
        ),
        migrations.AlterModelOptions(
            name='participationquestionchoice',
            options={'ordering': ('question', 'id')},
        ),
    ]

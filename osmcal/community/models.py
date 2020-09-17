from django.db import models


class Community(models.Model):
    name = models.CharField(max_length=120, verbose_name='Community Name')

    members = models.ManyToManyField('osmcal.User')
    events = models.ManyToManyField('osmcal.Event', related_name='communities')

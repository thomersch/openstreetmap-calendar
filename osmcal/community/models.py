from django.db import models


class Community(models.Model):
    name = models.CharField(max_length=120)

    members = models.ManyToManyField('osmcal.User')
    events = models.ManyToManyField('osmcal.Event')

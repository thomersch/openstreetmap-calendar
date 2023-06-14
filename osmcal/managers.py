from django.db import models

class HiddenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(hidden=False)

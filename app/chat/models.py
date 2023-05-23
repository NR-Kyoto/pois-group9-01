from django.db import models

# Create your models here.

class Audio(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(blank=True, null=True)
    fields = models.JSONField(blank=True, null=True)
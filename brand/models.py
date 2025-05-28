from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField(null=True)
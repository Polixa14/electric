from os import path
from electro.mixins.models import PKMixin
from django.db import models
from django.contrib.auth import get_user_model


def upload_to(instance, filename):
    _name, extension = path.splitext(filename)
    return f'articles/images/{str(instance.pk)}{extension}'


class ReferenceMaterial(PKMixin):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_to)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        ordering = ('name',)

from os import path
from electro.mixins.models import PKMixin
from django.db import models
from django.contrib.auth import get_user_model


def upload_to(instance, filename):
    _name, extension = path.splitext(filename)
    return f'articles/images/{str(instance.pk)}{extension}'


class Article(PKMixin):
    title = models.CharField(max_length=255)
    text = models.TextField()
    image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)


class Like(PKMixin):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_like = models.BooleanField(default=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'article')


class Comment(PKMixin):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created_at',)

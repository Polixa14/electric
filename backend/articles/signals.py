from django.dispatch import receiver
from django.db.models.signals import pre_save
from articles.models import Article
from django.utils.text import slugify


@receiver(pre_save, sender=Article)
def pre_save_slugify_article(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)

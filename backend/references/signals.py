from django.dispatch import receiver
from django.db.models.signals import pre_save
from references.models import ReferenceMaterial
from django.utils.text import slugify


@receiver(pre_save, sender=ReferenceMaterial)
def pre_save_slugify_article(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)

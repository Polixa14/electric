from django.db.models import TextChoices


class LineTypeChoices(TextChoices):
    CABLE = 'Cable', 'CABLE'
    WIRE = 'Wire', 'WIRE'

from django.contrib import admin
from references.models import ReferenceMaterial


@admin.register(ReferenceMaterial)
class ArticleAdmin(admin.ModelAdmin):
    pass
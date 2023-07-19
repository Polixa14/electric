from django.contrib import admin
from articles.models import Article, Like, Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

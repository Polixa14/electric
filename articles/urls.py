from django.urls import path, re_path
from articles.views import ArticleView, ArticleDetailView, LikeOrDislikeArticleView
from django.contrib.auth.views import LogoutView
from accounts.views import LoginView


urlpatterns = [
    path("", ArticleView.as_view(), name="articles"),
    path("article/<slug:slug>/",
         ArticleDetailView.as_view(),
         name='article_details'),
    re_path(r'article/(?P<slug>[-\w]+)/(?P<action>like|dislike)/',
            LikeOrDislikeArticleView.as_view(),
            name='article_action')
]
from rest_framework import routers
from apis.articles.views import ArticleViewSet, CommentViewSet

router = routers.SimpleRouter()
router.register(r'articles', ArticleViewSet, basename='articles')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'likes', CommentViewSet, basename='likes')
urlpatterns = router.urls

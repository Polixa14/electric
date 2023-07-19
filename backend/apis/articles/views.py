from articles.models import Article, Comment
from rest_framework import viewsets
from apis.permissions import IsAdminUserOrReadOnly, IsInstanceOwnerOrReadOnly
from apis.articles.serializers import ArticleSerializer, CommentSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsInstanceOwnerOrReadOnly,)

    def get_serializer(self, *args, **kwargs):
        kwargs['data'].update({
            "user": self.request.user.id
        })
        return super().get_serializer(*args, **kwargs)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsInstanceOwnerOrReadOnly,)

    def get_serializer(self, *args, **kwargs):
        kwargs['data'].update({
            "user": self.request.user.id
        })
        return super().get_serializer(*args, **kwargs)

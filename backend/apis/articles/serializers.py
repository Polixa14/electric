from rest_framework import serializers
from articles.models import Article, Comment
import base64


class ArticleSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    is_disliked_by_user = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    class Meta:
        model = Article
        fields = ('id', 'title', 'text', 'image', 'slug', 'created_at',
                  'updated_at', 'likes_count', 'dislikes_count',
                  'comments', 'is_liked_by_user', 'is_disliked_by_user')
        read_only_fields = ('id', 'created_at', 'updated_at', 'likes_count',
                            'dislikes_count', 'comments', 'is_liked_by_user',
                            'is_disliked_by_user', 'slug')
        extra_kwargs = {
            'title': {
                'required': True,
                'allow_blank': False
            },
            'text': {
                'required': True,
                'allow_blank': False
            },
        }

    def get_likes_count(self, instance):
        return instance.likes.filter(is_like=True).count()

    def get_dislikes_count(self, instance):
        return instance.likes.filter(is_like=False).count()

    def get_comments(self, instance):
        comments = []
        for comment in instance.comments.iterator():
            comments.append({
                "id": comment.id,
                "text": comment.text,
                "author": comment.user.email,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at
            })
        return comments

    def get_is_liked_by_user(self, instance):
        user = self.context['request'].user
        if user.is_authenticated:
            return instance.likes.filter(user=user, is_like=True).exists()

    def get_is_disliked_by_user(self, instance):
        user = self.context['request'].user
        if user.is_authenticated:
            return instance.likes.filter(user=user, is_like=False).exists()


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'user', 'text', 'article', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'user', 'is_like', 'article', 'created_at',
                  'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

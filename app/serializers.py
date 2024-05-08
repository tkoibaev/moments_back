from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id","username","bio","avatar","email")

class UserActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username',  'avatar')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')

class MomentSerializer(serializers.ModelSerializer):
    author = UserActionsSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField() # Добавлено поле для тегов

    class Meta:
        model = Moment
        fields = "__all__"

    def get_likes(self, obj):
        likes = Like.objects.likes_for_moment(obj.id)
        return LikeSerializer(likes, many=True).data

    def get_comments(self, obj):
        comments = Comment.objects.get_random_comments_for_moment(obj.id)
        return CommentSerializer(comments, many=True).data

    def get_tags(self, obj): # Метод для получения тегов
        tags = obj.tag.all()
        return TagSerializer(tags, many=True).data


class LikeSerializer(serializers.ModelSerializer):
    author = UserActionsSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'author', 'date_created')


class CommentSerializer(serializers.ModelSerializer):
    author = UserActionsSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = "__all__"

class SubscriptionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    subscriber = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('id', 'author', 'subscriber', 'date_created')

    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar
        }

    def get_subscriber(self, obj):
        return {
            'id': obj.subscriber.id,
            'username': obj.subscriber.username,
            'avatar': obj.subscriber.avatar
        }

from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id","username","bio","avatar","email")

class UserActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'avatar')

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
        author = obj.author
        return {
            'id': author.id,
            'username': author.username,
            'avatar': author.avatar.url if author.avatar else None  
        }

    def get_subscriber(self, obj):
        subscriber = obj.subscriber
        return {
            'id': subscriber.id,
            'username': subscriber.username,
            'avatar': subscriber.avatar.url if subscriber.avatar else None  
        }


class MomentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moment
        fields = ['description', 'image']

    def create(self, validated_data):
        # Извлекаем теги из валидированных данных
        tags = validated_data.pop('tag', [])
        print(tags)
        # Создаем момент без тегов
        moment = Moment.objects.create(**validated_data)
        
        # Добавляем теги к моменту
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            moment.tags.add(tag)
        
        return moment


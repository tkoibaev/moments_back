from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

class UserActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username',  'avatar')

class MomentSerializer(serializers.ModelSerializer):
    author = UserActionsSerializer(read_only=True)
    class Meta:
        model = Moment
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    author = UserActionsSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = "__all__"

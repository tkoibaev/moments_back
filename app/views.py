from django.shortcuts import render
from rest_framework.decorators import api_view 
from .models import * 
from .serializers import * 
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from django.core.exceptions import ObjectDoesNotExist


# Получение всех моментов
@api_view(['Get'])
def get_moments(request, format=None):
    moments = Moment.objects.get_top_moments()
    serializer = MomentSerializer(moments, many=True)
    return Response(serializer.data)

# Получение моментов конкретного юзера
@api_view(['Get'])
def get_user_moments(request, username, format=None):
    user_moments = Moment.objects.get_user_moments(username=username)
    serializer = MomentSerializer(user_moments, many=True)
    return Response(serializer.data)

# Поиск юзеров
@api_view(['Get'])
def get_users(request, format=None):
    search_query = request.GET.get('search', '')
    users = CustomUser.objects.filter(username__icontains=search_query)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# Инфа по юзеру
@api_view(['Get'])
def get_user(request, name, format=None):
    try:
        user = CustomUser.objects.get(username=name)
        subscriptions = Subscription.objects.get_subscriptions_for_user(name)
        subscribers = Subscription.objects.get_subscribers_for_user(name)
        
        # Сериализация данных
        user_serializer = UserSerializer(user)
        subscriptions_serializer = SubscriptionSerializer(subscriptions, many=True)
        subscribers_serializer = SubscriptionSerializer(subscribers, many=True)
        
        # Подготовка данных для ответа
        response_data = {
            'user': user_serializer.data,
            'subscriptions': subscriptions_serializer.data,
            'subscribers': subscribers_serializer.data,
        }
        return Response(response_data)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['GET'])
def get_moment_comments(request, pk, format=None):
    comments = Comment.objects.comments_for_moment(pk)
    serializer = CommentSerializer(comments, many=True) 
    return Response(serializer.data)

@api_view(['GET'])
def get_moments_by_tag(request, format=None):
    search_query = request.GET.get('search', '')
    if search_query:
        try:
            tag_obj = Tag.objects.get(name=search_query)
            moments = Moment.objects.filter(tag=tag_obj)
        except ObjectDoesNotExist:
            return Response([])
    else:
        moments = Moment.objects.order_by('?')[:20]
    
    serializer = MomentSerializer(moments, many=True)
    return Response(serializer.data)






# @api_view(['Post'])
# def post_moment(request, pk, format=None):
#     serializer = MomentSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

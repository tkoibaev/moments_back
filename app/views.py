from urllib import response
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from .models import * 
from .serializers import * 
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from django.core.exceptions import ObjectDoesNotExist
import redis
from django.conf import settings
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated


redis_session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


@api_view(['POST'])
def registrate(request):
    username = request.data['username']
    email = request.data['email']
    password = request.data['password']

    if not username:
        raise ValueError('The Username field must be set')
    if not email:
        raise ValueError('The Email field must be set')
    
    
    #проверяем логим и почту на уникальность
    if CustomUser.objects.filter(Q(username=username) | Q(email=email)).exists():
        return Response({'status': 'Exist'}, status=400)

    #валидируем пароль
    try:
        validate_password(password)
    except ValidationError as e:
        errors = list(e.messages)
        return Response({'password': errors}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(): # Проверяем валидность данных
        user = CustomUser.objects.create_user(username=username, password=password, email=email)
        random_key = str(uuid.uuid4())
        redis_session_storage.set(random_key, username)
        data = {
            "username": username,
            "email": email,
        }
        response = Response(data, status=status.HTTP_201_CREATED)
        response.set_cookie("session_id", random_key)
        return response
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

    random_key = str(uuid.uuid4())
    redis_session_storage.set(random_key, username)
    data = {
        "username": user.username,
        "email": user.email,
        "bio": user.bio, # Предполагается, что у вас есть поле bio в модели пользователя
        "avatar": user.avatar.url if user.avatar else None, # Предполагается, что у вас есть поле avatar в модели пользователя
    }
    response = Response(data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", random_key, samesite="Lax", max_age=30 * 24 * 60 * 60)
    return response

@api_view(['POST'])
def logout(request):
    session_id = request.COOKIES["session_id"]
    if session_id is None:
        message = {"message": "Token is not found in cookie"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)
    redis_session_storage.delete(session_id)
    response = Response({'message': 'Logged out successfully'})
    response.delete_cookie('access_token')

    return response

@api_view(['GET'])
def get_user_info(request):
    session_id = request.COOKIES.get('session_id', None)
    
    if not session_id:
        return Response({'error': 'No session ID found'}, status=400)
    
    # Попытка получить имя пользователя из Redis
    username = redis_session_storage.get(session_id).decode('utf-8')
    print(username)
    
    if not username:
        return Response({'error': 'Session expired or invalid'}, status=400)
    
    try:
        # Получение пользователя по имени пользователя
        user = CustomUser.objects.get(username=username)
        
        # Здесь вы можете дополнительно фильтровать поля, которые хотите вернуть
        data = {
            "username": user.username,
            "email": user.email,
            "bio": user.bio,  # Предполагается, что у вас есть поле bio в модели пользователя
            "avatar": user.avatar.url if user.avatar else None,  # Предполагается, что у вас есть поле avatar в модели пользователя
        }
        
        return Response(data, status=200)
    except ObjectDoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['PUT'])
def update_user_info(request):
    session_id = request.COOKIES.get('session_id', None)
    username = redis_session_storage.get(session_id).decode('utf-8')
    user = CustomUser.objects.get(username=username)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        redis_session_storage.set(session_id, serializer.instance.username.encode('utf-8'))
        
        data = {
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "avatar": user.avatar.url,
        }
        return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def add_moment(request):
    session_id = request.COOKIES.get('session_id', None)
    username = redis_session_storage.get(session_id).decode('utf-8')
    user = CustomUser.objects.get(username=username)
    serializer = MomentCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(author=user)  # Установка автора напрямую
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


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
@api_view(['GET'])
def get_user(request, name, format=None):
    session_id = request.COOKIES.get('session_id', None)
    username = redis_session_storage.get(session_id).decode('utf-8')
    user_me = CustomUser.objects.get(username=username)
    try:
        user = CustomUser.objects.get(username=name)
        subscriptions = Subscription.objects.get_subscriptions_for_user(name)
        subscribers = Subscription.objects.get_subscribers_for_user(name)
        
        # Сериализация данных
        user_serializer = UserSerializer(user)
        subscriptions_serializer = SubscriptionSerializer(subscriptions, many=True)
        subscribers_serializer = SubscriptionSerializer(subscribers, many=True)
        
        is_subscribed = Subscription.objects.filter(subscriber=user_me, author=user).exists()
        # Подготовка данных для ответа
        response_data = {
            'user': user_serializer.data,
            'subscriptions': subscriptions_serializer.data,
            'subscribers': subscribers_serializer.data,
            'is_subscribed' : is_subscribed,
        }
        return Response(response_data)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['POST'])
def toggle_like(request, moment_id):
    # Получаем session_id из куки
    session_id = request.COOKIES.get('session_id', None)
    username = redis_session_storage.get(session_id).decode('utf-8')
    user = CustomUser.objects.get(username=username)
    # Пытаемся получить момент по ID
    try:
        moment = Moment.objects.get(id=moment_id)
    except Moment.DoesNotExist:
        return Response({'error': 'Moment not found'}, status=404)

    # Тoggles like
    success = Like.objects.toggle_like(user, moment)
    if success:
        return Response({'success': 'Like toggled'})
    else:
        return Response({'error': 'Like already exists or was removed'}, status=400)

@api_view(['POST'])
def add_comment(request, moment_id):
    # Получаем данные комментария из запроса
    content = request.data.get('content')
    if not content:
        return Response({'error': 'Content is required'}, status=400)

    # Получаем пользователя из куки
    session_id = request.COOKIES.get('session_id', None)
    username = redis_session_storage.get(session_id).decode('utf-8')
    user = CustomUser.objects.get(username=username)
    print(content)
    # Пытаемся получить момент по ID
    try:
        moment = Moment.objects.get(id=moment_id)
    except Moment.DoesNotExist:
        return Response({'error': 'Moment not found'}, status=404)

    # Добавляем комментарий
    comment = Comment.objects.add_comment(user, moment, content)
    return Response({'success': 'Comment added', 'comment_id': comment.id})


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




@api_view(['POST'])
def toggle_subscription(request, name):
    session_id = request.COOKIES.get('session_id', None)
    username = redis_session_storage.get(session_id).decode('utf-8')
    subscriber = CustomUser.objects.get(username=username)
    
    try:
        author = CustomUser.objects.get(username=name)
    except ObjectDoesNotExist:
        return Response({'error': 'Author not found'}, status=404)
    
    # Используем менеджер модели для вызова метода toggle_subs
    Subscription.objects.toggle_subs(subscriber, author)
    return Response({'success': 'Subscription status toggled'}, status=200)

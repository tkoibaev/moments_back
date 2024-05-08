from app import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/moments/', views.get_moments, name='all_moments_list'),#GET - список всех моментов - OK
    path('api/moments_by_user/<str:username>/', views.get_user_moments, name='user_moments_list'),#GET - список всех моментов пользователя -OK
    # path('api/moments/post/')
    # path('api/moments/delete/<int:pk>')

    path('api/users/', views.get_users,name='get_users'), #GET - список юзеров с поиском по имени - OK
    path('api/user/<str:name>/', views.get_user,name='get_user'), #GET - инфа по юзеру и его подписки/подписчики по имени - OK
    path('api/moments/tag/', views.get_moments_by_tag, name='get_moments_by_tag'),

    path('api/comments/<int:pk>/', views.get_moment_comments,name="get_moment_comments") #GET - список комментов к моменту - OK
]

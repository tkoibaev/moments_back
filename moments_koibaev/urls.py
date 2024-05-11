from app import views
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/register/', views.registrate, name='registrate'),#POST - регистрация
    path('api/login/', views.login, name='login'),#POST - логин
    path('api/logout/', views.logout, name='logout'),#POST - логин
    path('api/user_info/', views.get_user_info, name='get_user_info'),#POST - логин

    path('api/update_user_info/', views.update_user_info, name='update_user_info'),#POST - логин



    path('api/moments/', views.get_moments, name='all_moments_list'),#GET - список всех моментов - OK
    path('api/moments_by_user/<str:username>/', views.get_user_moments, name='user_moments_list'),#GET - список всех моментов пользователя -OK
    # path('api/moments/post/')
    # path('api/moments/delete/<int:pk>')

    path('api/users/', views.get_users,name='get_users'), #GET - список юзеров с поиском по имени - OK
    path('api/user/<str:name>/', views.get_user,name='get_user'), #GET - инфа по юзеру и его подписки/подписчики по имени - OK
    path('api/moments/tag/', views.get_moments_by_tag, name='get_moments_by_tag'),

    path('api/comments/<int:pk>/', views.get_moment_comments,name="get_moment_comments") #GET - список комментов к моменту - OK
]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
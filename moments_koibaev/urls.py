from app import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/moments/', views.get_moments, name='all-moments-list'),#GET - список всех моментов
    # path('api/moments/post/')
    # path('api/moments/delete/<int:pk>')
    path('api/user_moments/<int:pk>/', views.get_user_moments, name='user-moments-list'),#GET - список всех моментов пользователя


]

from django.urls import path, include
from . import views

urlpatterns = [
    path('user/register/', views.register_user, name='register_user'),
    path('user/login/', views.user_login, name='user_login'),
    path('user/logout/', views.user_logout, name='user_logout'),
    path('user/current/', views.get_current_user_info, name='get_current_user_info'),
    path('user/<int:user_id>/', views.get_user_by_id, name='get_user_by_id'),
    path('user/address/', views.update_user_address, name='update_user_address'),
]
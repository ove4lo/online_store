from django.urls import path, include
from django.contrib import admin
from User.views import *


urlpatterns = [
    path('user/create/', create_user)
]

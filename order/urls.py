from django.urls import path, include
from django.contrib import admin
from order.views import *


urlpatterns = [
    path('order/create/', create_order)
]

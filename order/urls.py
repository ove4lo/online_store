from django.urls import path, include
from django.contrib import admin
from order.views import *


urlpatterns = [
    path('order/create/', create_order),
    path('order/<int:order_id>/', get_order_by_id)
]

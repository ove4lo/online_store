from django.urls import path, include
from django.contrib import admin
from .views import *


# url пока не готова авторизация, для теста
urlpatterns = [
    path('get_cart/', get_cart, name='get_cart'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>', remove_from_cart, name='remove_from_cart'),
    path('update_cart_item_quantity/', update_cart_item_quantity, name='update_cart_item_quantity'),
]
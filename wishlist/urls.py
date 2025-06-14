from django.urls import path, include
from django.contrib import admin
from .views import get_wishlist, remove_from_wishlist, add_to_wishlist, clear_wishlist

urlpatterns = [
    path('get_wishlist/', get_wishlist),
    path('remove_from_wishlist/<int:product_id>/', remove_from_wishlist),
    path('add_to_wishlist/', add_to_wishlist),
    path('clear_wishlist/', clear_wishlist),

]
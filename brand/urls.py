from django.urls import path, include
from django.contrib import admin
from .views import *

urlpatterns = [
    path('brand/', get_all_brands, name='get_all_brands'),
    path('brand/create/', create_brand, name='create_brand'),
    path('brand/update/<int:id>', update_brand, name='update_brand'),
    path('brand/delete/<int:id>', delete_brand, name='delete_brand'),
]
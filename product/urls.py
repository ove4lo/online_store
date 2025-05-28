from django.urls import path
from django.contrib import admin
from product.views import *


urlpatterns = [
    path('products/', get_all_products)
]

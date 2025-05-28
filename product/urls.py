from django.urls import path
from django.contrib import admin
from product.views import *


urlpatterns = [
    path('/api/products/', get_all_products)
]

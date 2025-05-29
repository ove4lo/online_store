from django.urls import path
from django.contrib import admin
from product.views import *


urlpatterns = [
    path('products/', get_all_products),
    path('products/create/', create_product),
    path('products/delete/<int:product_id>/', delete_product)
]

from django.urls import path
from django.contrib import admin
from product.views import *


urlpatterns = [
    path('products/', get_all_products),
    path('products/<int:product_id>/', get_product_by_id),
    path('products/create/', create_product),
    path('products/soft-delete/<int:product_id>/', soft_delete_product),
    path('products/hard-delete/<int:product_id>/', hard_delete_product),
    path('products/edit/<int:product_id>/', edit_product)
]
